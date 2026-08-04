# Resumen Ejecutivo y Cheatsheet — Chip Huyen AI Engineering

## ⚡ Guía Rápida de Arquitectura

| Necesidad | Solución Recomendada | Tecnología / Herramientas |
| --- | --- | --- |
| **Acceso a datos corporativos dinámicos** | RAG Avanzado (Hybrid Search + Re-ranking) | BM25 + Qdrant / Pinecone + Cross-Encoder |
| **Garantizar salida en JSON estructurado** | Native Structured Outputs / Pydantic | OpenAI JSON Schema, Instructor, Outlines |
| **Reducir latencia y costos de inferencia** | Cuantización INT4 + vLLM + Speculative Decoding | vLLM, TensorRT-LLM, AWQ, Draft Models |
| **Especializar modelo en formato/dominio** | PEFT / LoRA (Low-Rank Adaptation) | Unsloth, Hugging Face PEFT, QLoRA |
| **Prevenir ejecuciones no autorizadas** | Guardrails Doblados + Human-in-the-loop | Llama Guard, Guardrails AI, Instructor |
| **Diagnóstico de fallas en flujos agénticos** | Tracing & Telemetría estructurada | LangSmith, Phoenix Arize, OpenTelemetry |
| **Evaluación automatizada en CI/CD** | LLM-as-a-Judge con rúbricas estrictas | RAGAS, DeepEval, Promptfoo |
