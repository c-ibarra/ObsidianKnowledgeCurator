# Modelos Mentales y Principios de Diseño — Chip Huyen

1. **La Paradoja del 80/20**: El primer 80% de una aplicación de IA se logra en horas con una API; el 20% restante (alucinaciones, latencia, costos, seguridad) requiere meses de ingeniería rigurosa.
2. **Software Estocástico**: Tratar al modelo no como una función determinista, sino como una distribución probabilística de salidas que requiere guardarraíles y harness de evaluación continua.
3. **Evaluation-Driven Development (EDD)**: No puedes mejorar lo que no puedes medir. Construir el testset y el harness de evaluación ANTES de optimizar los prompts o modelos.
4. **Context Engineering sobre Feature Engineering**: En Software 3.0, la ventaja competitiva radica en seleccionar, estructurar y comprimir el contexto inyectado al modelo en lugar de crear features manuales.
5. **RAG para Conocimiento, Finetuning para Formato**: Usar RAG cuando los hechos son dinámicos; usar Finetuning para fijar sintaxis, estilo o reducir latencia.
6. **Defensa en Profundidad en Seguridad**: Asumir que los modelos son vulnerables por diseño a Prompt Injection e implementar guardarraíles acotados con Human-in-the-loop.
7. **El Volante de Retroalimentación (Data Flywheel)**: Los modelos son commodities; los bucles de feedback de producción y telemetría de usuario son ventajas inexpugnables.
