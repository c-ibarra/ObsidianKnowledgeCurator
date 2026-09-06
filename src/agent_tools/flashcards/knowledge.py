"""Knowledge Unit extraction, batching, and evidence verification."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from src.agent_tools.flashcards.models import (
    KnowledgeUnit,
    SectionNode,
    SourceSpan,
    UnitType,
)


def build_extraction_batches(
    sections: List[SectionNode],
    max_chars_per_batch: int = 4000,
) -> List[Dict[str, Any]]:
    """Groups section spans into manageable batches for LLM / semantic extraction."""
    batches: List[Dict[str, Any]] = []
    current_batch_spans: List[SourceSpan] = []
    current_chars = 0
    current_doc_id = ""
    current_heading = ""

    def flush_batch() -> None:
        nonlocal current_batch_spans, current_chars
        if not current_batch_spans:
            return

        batch_id = f"batch_{current_doc_id[:8]}_{len(batches)}"
        batch_data = {
            "batch_id": batch_id,
            "document_id": current_doc_id,
            "heading_path": current_heading,
            "spans": [
                {
                    "span_id": s.span_id,
                    "heading_path": s.heading_path,
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "text": s.text_content,
                }
                for s in current_batch_spans
            ],
            "formatted_context": "\n\n".join(
                f"[{s.span_id}] ({s.heading_path} L{s.start_line}-{s.end_line}):\n{s.text_content}"
                for s in current_batch_spans
            ),
        }
        batches.append(batch_data)
        current_batch_spans = []
        current_chars = 0

    for sec in sections:
        for span in sec.spans:
            text_len = len(span.text_content)
            if current_doc_id != span.document_id or (current_chars + text_len > max_chars_per_batch and current_batch_spans):
                flush_batch()

            current_doc_id = span.document_id
            current_heading = span.heading_path
            current_batch_spans.append(span)
            current_chars += text_len

    flush_batch()
    return batches


def validate_knowledge_unit(
    data: Dict[str, Any],
    available_spans: Dict[str, SourceSpan],
    document_id: str,
) -> Tuple[Optional[KnowledgeUnit], Optional[str]]:
    """Validates that an extracted Knowledge Unit complies with evidence citations."""
    concept = str(data.get("concept", "")).strip()
    explanation = str(data.get("explanation", "")).strip()

    if not concept:
        return None, "Missing 'concept' field"
    if not explanation:
        return None, "Missing 'explanation' field"

    raw_type = str(data.get("unit_type", "definition")).lower()
    try:
        unit_type = UnitType(raw_type)
    except ValueError:
        unit_type = UnitType.DEFINITION

    evidence_spans = data.get("evidence_spans", [])
    if isinstance(evidence_spans, str):
        evidence_spans = [evidence_spans]

    valid_spans: List[str] = []
    for sid in evidence_spans:
        sid_clean = sid.strip("[] ,")
        if sid_clean in available_spans:
            valid_spans.append(sid_clean)

    claims = data.get("claims", [])
    if isinstance(claims, str):
        claims = [claims]

    conditions = data.get("conditions", [])
    exceptions = data.get("exceptions", [])

    ku = KnowledgeUnit.create(
        concept=concept,
        explanation=explanation,
        source_document_id=document_id,
        unit_type=unit_type,
        claims=claims,
        evidence_spans=valid_spans,
    )
    ku.conditions = conditions
    ku.exceptions = exceptions

    return ku, None


def extract_deterministic_units(
    spans: List[SourceSpan],
    document_id: str,
) -> List[KnowledgeUnit]:
    """Fallback / rule-based extractor that discovers core concepts, definitions,

    and formulas from spans when running without interactive LLM prompts.
    """
    units: List[KnowledgeUnit] = []
    seen_concepts = set()

    # Regex for definitions: **Concept**: Explanation or Concept - Explanation
    def_regex = re.compile(r"^\s*[-*]?\s*\*\*([^*]+)\*\*\s*[:—–-]\s*(.+)$", re.MULTILINE)
    # Regex for math formulas: $$ ... $$
    math_regex = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)

    for span in spans:
        # Check math formulas
        for m in math_regex.finditer(span.text_content):
            formula = m.group(1).strip()
            concept_name = f"Formula: {span.heading_path.split(' / ')[-1]}"
            if concept_name.lower() not in seen_concepts:
                seen_concepts.add(concept_name.lower())
                ku = KnowledgeUnit.create(
                    concept=concept_name,
                    explanation=f"Mathematical formulation:\n$${formula}$$",
                    source_document_id=document_id,
                    unit_type=UnitType.FORMULA,
                    evidence_spans=[span.span_id],
                )
                units.append(ku)

        # Check bold definitions
        for m in def_regex.finditer(span.text_content):
            concept = m.group(1).strip()
            explanation = m.group(2).strip()
            if len(concept) > 2 and len(explanation) > 10:
                if concept.lower() not in seen_concepts:
                    seen_concepts.add(concept.lower())
                    ku = KnowledgeUnit.create(
                        concept=concept,
                        explanation=explanation,
                        source_document_id=document_id,
                        unit_type=UnitType.DEFINITION,
                        evidence_spans=[span.span_id],
                    )
                    units.append(ku)

        # Check key takeaways numbered items
        if "Key Takeaways" in span.heading_path or "Takeaways" in span.heading_path:
            for line in span.text_content.splitlines():
                line = line.strip()
                match = re.match(r"^\d+\.\s*(.+)$", line)
                if match:
                    takeaway = match.group(1).strip()
                    title_match = re.match(r"^\*\*([^*]+)\*\*\s*[:—–-]?\s*(.+)$", takeaway)
                    if title_match:
                        c_title = title_match.group(1).strip()
                        c_expl = title_match.group(2).strip()
                    else:
                        c_title = takeaway[:50] + ("..." if len(takeaway) > 50 else "")
                        c_expl = takeaway

                    if c_title.lower() not in seen_concepts:
                        seen_concepts.add(c_title.lower())
                        ku = KnowledgeUnit.create(
                            concept=c_title,
                            explanation=c_expl,
                            source_document_id=document_id,
                            unit_type=UnitType.FACT,
                            evidence_spans=[span.span_id],
                        )
                        units.append(ku)

        # Check key questions (e.g. "Preguntas Clave", "Key Questions", "Preguntas")
        is_question_section = any(
            q_token in span.heading_path.lower()
            for q_token in ("preguntas clave", "key questions", "preguntas", "inquiry questions")
        )
        if is_question_section:
            # Build an answer index from other explanatory spans in this document
            doc_spans = [s for s in spans if s.span_id != span.span_id]
            
            for line in span.text_content.splitlines():
                line = line.strip()
                match = re.match(r"^\d+\.\s*(.+)$", line)
                if match:
                    question_text = match.group(1).strip()
                    if len(question_text) > 10 and question_text.lower() not in seen_concepts:
                        seen_concepts.add(question_text.lower())
                        
                        # Find best matching explanatory context across document spans
                        q_words = [w.lower() for w in re.findall(r"\b[A-Za-zÁÉÍÓÚáéíóúÑñ]{4,}\b", question_text)]
                        best_answer = ""
                        best_score = 0
                        best_span_id = span.span_id

                        for candidate_span in doc_spans:
                            content = candidate_span.text_content
                            if "## 3." in candidate_span.heading_path or "Resumen" in candidate_span.heading_path or "Desarrollo" in candidate_span.heading_path:
                                matches = sum(1 for w in q_words if w in content.lower())
                                if matches > best_score and len(content.strip()) > 30:
                                    best_score = matches
                                    # Pick the most relevant paragraphs
                                    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                                    rel_p = [p for p in paragraphs if any(w in p.lower() for w in q_words)]
                                    best_answer = "\n\n".join(rel_p[:2]) if rel_p else paragraphs[0]
                                    best_span_id = candidate_span.span_id

                        if not best_answer or len(best_answer) < 30:
                            best_answer = f"Ver desarrollo del tema en el capítulo correspondiente."

                        ku = KnowledgeUnit.create(
                            concept=question_text,
                            explanation=best_answer,
                            source_document_id=document_id,
                            unit_type=UnitType.QUESTION,
                            evidence_spans=[best_span_id],
                        )
                        units.append(ku)

        # Check Obsidian Callouts (> [!example], > [!quote], > [!warning], > [!tip])
        callout_matches = re.finditer(r"^>\s*\[!(\w+)\]\s*(.+?)\n((?:>.*\n?)+)", span.text_content, re.MULTILINE)
        for c_match in callout_matches:
            c_type = c_match.group(1).strip()
            c_title = c_match.group(2).strip()
            c_body = re.sub(r"^>\s?", "", c_match.group(3), flags=re.MULTILINE).strip()
            if len(c_title) > 3 and len(c_body) > 20:
                callout_concept = f"Caso / Principio: {c_title}"
                if callout_concept.lower() not in seen_concepts:
                    seen_concepts.add(callout_concept.lower())
                    ku = KnowledgeUnit.create(
                        concept=callout_concept,
                        explanation=f"[{c_type.upper()}] {c_body}",
                        source_document_id=document_id,
                        unit_type=UnitType.FACT,
                        evidence_spans=[span.span_id],
                    )
                    units.append(ku)

    return units

