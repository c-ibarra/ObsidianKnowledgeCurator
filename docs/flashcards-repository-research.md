# Investigación: fuentes, persistencia y flashcards

Investigación del repositorio actual para diseñar una extensión nativa de `obsidianKnowledgeCurator`. No se implementa funcionalidad ni se inspecciona el contenido del Vault externo. Los componentes nuevos mencionados son propuestas, no capacidades actuales.

## Evidencia existente

| Área | Referencia | Hallazgo y límite |
|---|---|---|
| Configuración | `src/config.py:17`, `:39`, `:68`, `:81` | Carga `.env`, resuelve Vault y centraliza rutas/protegidos. Reutilizable. |
| SQLite | `scripts/vault_db.py:18`, `:27` | Conexión con WAL/foreign keys; tablas `files`, `links`, `contradictions`. No tablas de unidades, mazos, tarjetas o ejecuciones. |
| Incremental | `scripts/vault_db.py:252`, `:290`, `:301` | Detecta cambios por mtime; `target_folder` filtra actualizaciones después de escanear todo el Vault. No hashes ni detección de renames. |
| Metadata | `scripts/vault_db.py:81`, `:110` | Regex para blockquote, wikilinks y contradicciones. Elimina alias/anclas; no distingue embeds ni resuelve ambigüedades. No AST Markdown. |
| Exclusiones | `scripts/vault_db.py:16`; `scripts/graphify_helper.py:38` | Excluyen carpetas ocultas específicas, pero no aplican `PROTECTED_ZONES`. No reutilizar como escaneo autorizado sin filtro adicional. |
| Grafo | `scripts/graphify_helper.py:44`, `:80`, `:93`, `:195` | Extractor externo Graphify, cache JSON por mtime y contexto `source_file`. La actualización individual reconstruye el grafo global. No embeddings identificados en este módulo. |
| Segmentación | `src/agent_tools/book_ingestion/engine.py:71`, `:207` | `BookIngestionService.detect_chapters` devuelve capítulos con título, contenido, tokens y menciones de figuras. Fallback ~2000 palabras. No jerarquía, source spans, IDs o límite duro para capítulos/párrafos grandes. |
| Tokens | `src/agent_tools/book_ingestion/engine.py:27` | Intenta tiktoken/cl100k_base y luego heurística palabras/0.75. No cuenta exacta de tokens Gemini. |
| Documentos | `src/agent_tools/anydoc_engine.py:109` | Conversión multi-formato AnyDoc y fallback pypdf. Devuelve dict, no schema estricto. No preserva procedencia espacial/página de forma contractual. |
| Media | `src/agent_tools/anydoc_engine.py:51`, `:128`, `:137` | Escribe imágenes inmediatamente en assets/images con slug e índice. Retorna nombres sin asociación figura/página. `vault_root=None` intenta resolver el Vault: no significa modo sin escritura. |
| Errores PDF | `src/agent_tools/anydoc_engine.py:94`, `:176`, `:207` | Fallback puede retornar texto de error y ser anunciado como success=True. No OCR real identificado aquí, pese a la etiqueta del texto generado. |
| Q/A | `scripts/safe_merge.py:137` | `merge_flashcards` acepta Q:/A:, deduplica pregunta case-insensitive y conserva respuesta antigua. No permite actualización semántica fiable ni preserva IDs/historial. |
| Merge Markdown | `scripts/safe_merge.py:14`, `:281` | Secciones detectadas por líneas que empiezan con #, incluso dentro de fences. No AST pese al nombre de la CLI. Conservar para compatibilidad legacy. |
| Hash | `src/agent_tools/note_normalizer.py:54` | SHA256 normalizado con eliminación opcional de encabezado. Útil para duplicados legacy; insuficiente como hash de revisión fiel de fuente. |
| Watcher | `scripts/graphify_watcher.py:24`, `:39`, `:115` | Watchdog con cola en memoria y debounce. Solo Markdown; no imágenes. Vacía cola antes de procesar. No scheduler durable ni checkpoint manager. |
| Huérfanos | `scripts/okc_doctor.py:172`, `:187`, `:199` | Considera referencias de imágenes únicamente encontradas en Markdown. Un mazo solo JSON puede dejar media activa expuesta a archivo como huérfana. |

## APIs aprovechables

- `get_vault_db_connection(db_path=DB_PATH)`: conexión SQLite existente.
- `parse_note_metadata(content, rel_path)`: metadatos convencionales, complementando un parser estructural nuevo.
- `BookIngestionService.detect_chapters(text)`, `estimate_tokens(text)`, `detect_figures(text)`: ayudas de segmentación y estimación.
- `convert_document_to_markdown(file_path, vault_root=None, slug="document")`: conversión existente, tras separar extracción y publicación para el nuevo flujo.
- `merge_flashcards(old_lines, new_lines)`: referencia para importación Q/A legacy; no DeckWriter de UPDATE.
- `compute_content_hash(content, strip_header=True)`: deduplicación de notas legacy, separada del hash crudo de procedencia.

## Gaps y propuestas

1. Nuevo paquete propuesto `src/agent_tools/flashcards/` para contratos Pydantic, parsing estructural, planificación determinista y persistencia específica. No una aplicación o cadena de agentes paralela.
2. Reutilizar SQLite con tablas `study_*` y migraciones versionadas. IDs propios para fuentes y unidades; evitar cascadas desde el índice reconstruible que destruyan trazabilidad.
3. Parser con secciones jerárquicas, source spans, tablas/fórmulas/fences, links y embeds. El scanner debe limitar alcance, resolver rutas canónicas, excluir zonas protegidas y detectar ambigüedades.
4. AnyDoc con modo staging explícito y errores tipados, preservando comportamiento legacy por defecto. No tratar error de PDF como conocimiento. OCR no identificado en este módulo.
5. Mantener fuente cruda y su hash. Evitar sanitización global de fórmulas/código: el agente principal identificó que el sanitizer elimina U+2061/U+2062 y ZWJ, lo que puede modificar significado.
6. Writer de mazo Markdown con IDs en comentarios y estado SQLite. Adaptar comprobación de media activa o asegurar embeds legibles por doctor. Backend Anki/SRS: no identificado en los módulos inspeccionados.
7. Estado durable fuera de `temp/`; staging por ejecución dentro de `temp/`, limpiando únicamente artefactos propios finalizados. Journal PREPARED/COMMITTED y reconciliación: SQLite y filesystem no forman una sola transacción atómica.
8. No disparar generación LLM por cada evento watcher. La invalidación de fuentes y la decisión de regenerar deben estar separadas.

## Tests y dependencias

El agente principal ejecutó de forma aislada **4 tests unittest de book_ingestion y 6 tests de safe_merge: todos pasan**. Esto valida comportamiento existente básico, no la funcionalidad propuesta.

Referencias adicionales: `tests/test_note_normalizer.py:23` prueba hashes; `:104` archivo seguro; `tests/test_okc_doctor.py:175` media huérfana. Estilos mixtos unittest y funciones de pytest.

`pyproject.toml` declara Python >=3.12, Pydantic, pypdf, firecrawl-anydoc, watchdog, requests y MCP. No declara directamente un parser Markdown AST; comprobar disponibilidad transitiva y contrato antes de decidir una dependencia nueva.

Tests faltantes para la extensión: parser con posiciones; fórmulas/código intactos; media ambigua/inexistente; cambios binarios; renames; repetición sin duplicados; conservación de tarjetas humanas; fallos entre PREPARED/publicación/COMMITTED; reanudación; cambios concurrentes; cobertura y fidelidad pedagógica con outputs LLM controlados.

## Convenciones y límites de la investigación

Se leyó `GEMINI.md`: encabezados blockquote y sin YAML en notas; media en assets/images; protegidos excluidos de escaneo; staging en temp y limpieza final. Contiene instrucciones operativas tanto de preferencia CLI como bypass filesystem nativo por un problema de sandbox; no demuestra un SDK programático de Antigravity.

**No identificado en el repositorio actual**, dentro de los módulos inspeccionados: contrato de SDK Antigravity para LLM, motor durable de tareas, flashcards con repetición espaciada, exportador Anki y resolvedor completo de media Obsidian. El diseño debe marcar tales capacidades como nuevas u opcionales, sin asumirlas existentes.
