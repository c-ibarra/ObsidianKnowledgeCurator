# Glosario Especializado — AI Engineering (Chip Huyen)

- **AI Engineering (Ingeniería de IA)**: Disciplina de ingeniería de sistemas centrada en componer, evaluar, orquestar y optimizar modelos de fundamentación preentrenados para construir aplicaciones de producción confiables y escalables.
- **Foundation Models (Modelos de Fundamentación)**: Modelos masivos de aprendizaje profundo preentrenados sobre petabytes de datos no estructurados (LLMs, LMMs) que poseen capacidades generales de razonamiento y procesamiento de lenguaje.
- **Context Engineering (Ingeniería de Contexto)**: Conjunto de técnicas (RAG, filtrado, formateo, compresión de ventana de atención) para estructurar el prompt de entrada e inyectar la información precisa que el modelo necesita para responder.
- **RAG (Retrieval-Augmented Generation)**: Arquitectura que combina la recuperación de documentos externos desde una base de datos vectorial o motor de búsqueda léxico con la capacidad de generación de un LLM.
- **PEFT (Parameter-Efficient Fine-Tuning)**: Métodos de ajuste fino (como LoRA o QLoRA) que modifican únicamente un pequeño porcentaje de parámetros adicionales o matrices de bajo rango, congelando los pesos originales del modelo.
- **LoRA (Low-Rank Adaptation)**: Técnica de PEFT que descompone la matriz de actualización de pesos $\Delta W$ en dos matrices de bajo rango $B \cdot A$, reduciendo drásticamente el consumo de VRAM y tiempo de cómputo.
- **LLM-as-a-Judge**: Patrón de evaluación donde un modelo de fundamentación de alta capacidad (modelo de frontera) evalúa y califica automáticamente las respuestas de otros modelos según una rúbrica estructurada.
- **Prompt Injection**: Vulnerabilidad de seguridad donde texto malicioso (directo o indirecto) altera las instrucciones originales del sistema en un LLM, provocando comportamientos no autorizados.
- **PagedAttention**: Algoritmo de gestión de memoria para servidores de inferencia (vLLM) que almacena el KV Cache en bloques de memoria virtual discontinuos, eliminando la fragmentación de VRAM.
- **Speculative Decoding**: Técnica de aceleración de inferencia que utiliza un modelo pequeño borrador (Draft Model) para sugerir tokens que luego son validados en paralelo por el modelo grande (Target Model).
