# Flashcards de Repetición Espaciada — [[AI Engineering (Chip Huyen)]]

#flashcard

Q: ¿Cuál es la diferencia fundamental entre Software 1.0, 2.0 y 3.0 según Chip Huyen?
A: Software 1.0 usa reglas explícitas escritas por humanos. Software 2.0 usa datos etiquetados para entrenar modelos supervisados (ML tradicional). Software 3.0 usa modelos de fundamentación preentrenados combinados con ingeniería de contexto, prompts y agentes.

Q: ¿Por qué la inferencia de LLMs está limitada por la memoria (Memory-bandwidth bound)?
A: Porque la generación autorregresiva token por token requiere transferir todos los parámetros del modelo (e.g., 140 GB en FP16) desde la VRAM a los Tensor Cores de la GPU para predecir un solo token.

Q: ¿Qué es LoRA (Low-Rank Adaptation) y cuál es su ventaja matemática?
A: Es una técnica de PEFT que congela los pesos originales del modelo $W_0$ e inyecta matrices de descomposición de bajo rango $B \cdot A$ (con rango $r \ll \min(d,k)$). Reduce los parámetros entrenables en más del 99% sin perder precisión.

Q: ¿Cuáles son las 5 fases de un sistema RAG Avanzado para producción?
A: 1. Transformación de Consulta (Rewriting / HyDE). 2. Búsqueda Híbrida (Dense Embeddings + BM25). 3. Re-ranking con Cross-Encoder. 4. Compresión y Formateo de Contexto. 5. Generación por el LLM.

Q: ¿Qué es el fenómeno "Lost in the Middle" en la ventana de contexto de los LLMs?
A: Es la tendencia probabilística de los modelos a prestar máxima atención a la información al inicio y final del prompt, degradando la capacidad de recuperar información ubicada en el centro de un contexto largo.

Q: ¿Cuáles son los 4 sesgos principales del patrón LLM-as-a-Judge?
A: 1. Position Bias (Sesgo de Posición). 2. Verbosity Bias (Sesgo de Verbosidad). 3. Self-Enhancement Bias (Sesgo de Auto-preferencia). 4. Length & Format Preference (Sesgo de Formato).

Q: ¿Qué diferencia existe entre Direct Prompt Injection e Indirect Prompt Injection?
A: La inyección directa ocurre cuando el usuario introduce órdenes para sobrescribir las instrucciones en el prompt. La inyección indirecta ocurre cuando un documento o página web recuperada por RAG contiene instrucciones maliciosas ocultas que el LLM ejecuta.

Q: ¿Cómo optimiza PagedAttention (vLLM) la memoria GPU durante la inferencia?
A: Aplica el principio de memoria virtual de los sistemas operativos asignando bloques no continuos de VRAM para almacenar el KV Cache, eliminando la fragmentación de memoria y aumentando hasta 4x la capacidad de usuarios concurrentes.

Q: ¿En qué consiste el Decodificado Especulativo (Speculative Decoding)?
A: Utiliza un modelo borrador ultra-rápido y pequeño (Draft Model) para generar una ráfaga de tokens candidatos que luego son validados en paralelo en un solo paso por el modelo grande (Target Model), acelerando la inferencia en 2-3x.

Q: ¿Qué es el Data & AI Flywheel (Volante de Retroalimentación)?
A: Es el proceso continuo de capturar la telemetría e interacción implícita/explícita de los usuarios en producción para alimentar los datasets de evaluación (Testsets) y reentrenamiento (Fine-Tuning), creando una ventaja competitiva defensible.

Q: ¿Por qué BLEU y ROUGE son insuficientes para evaluar la calidad de los LLMs?
A: Porque solo miden coincidencias de n-gramas léxicos exactos. No comprenden similitud semántica ni detectan alucinaciones factuales sutiles (como negar un hecho agregando una sola palabra).

Q: ¿Cuáles son los 3 patrones agénticos principales identificados por Chip Huyen?
A: 1. ReAct (Reasoning + Acting). 2. Plan-and-Execute. 3. Multi-Agent Orchestration.

Q: ¿Cuándo se debe elegir RAG sobre Finetuning?
A: RAG se elige cuando se requiere acceso a información dinámica cambiante, transparencia con citas de fuentes o cuando el costo de re-entrenamiento es insostenible. Finetuning se elige para fijar formato, estilo, tono o reducir latencia en tareas específicas.

Q: ¿Qué es la cuantización de pesos (AWQ / GPTQ)?
A: Es la reducción de la precisión numérica de los parámetros del modelo (de FP16/BF16 a INT8/INT4), reduciendo la huella de VRAM a la cuarta parte con una pérdida de precisión prácticamente imperceptible.

Q: ¿Qué es el principio de Human-in-the-loop (HITL) en sistemas agénticos?
A: Es el requerimiento arquitectónico de solicitar la confirmación humana explícita antes de que un agente ejecute acciones críticas o irreversibles (compras, envíos de email, modificaciones de base de datos).
