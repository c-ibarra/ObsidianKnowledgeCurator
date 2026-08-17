import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.config import VAULT_ROOT
BOOKS_ROOT = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/raw/Books"
MAIN_NOTE_PATH = BOOKS_ROOT / "Anna Papalia — Interviewology The New Science of Interviewing.md"
WIKI_ROOT = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/wiki"

os.makedirs(BOOKS_ROOT, exist_ok=True)
os.makedirs(WIKI_ROOT, exist_ok=True)

# -----------------------------------------------------------------------------
# MAIN EXECUTIVE NOTE
# -----------------------------------------------------------------------------
main_note_content = """# Anna Papalia — Interviewology The New Science of Interviewing

> **Anna Papalia — Interviewology: The New Science of Interviewing**
> Tipo: libro | no-ficción
> Procesado: 13-08-2026
> Estado: [[Chapter 00 — Front Matter and Foundations]], [[Chapter 01 — An Interview Can Change Your Life]], [[Chapter 02 — How I Discovered the Four Interview Styles]], [[Chapter 03 — Why Its Important to Know Your Interview Style]], [[Chapter 04 — The Four Interview Styles]], [[Chapter 05 — The Charmer]], [[Chapter 06 — Interviewing with a Charmer]], [[Chapter 07 — The Challenger]], [[Chapter 08 — Interviewing with a Challenger]], [[Chapter 09 — The Examiner]], [[Chapter 10 — Interviewing with an Examiner]], [[Chapter 11 — The Harmonizer]], [[Chapter 12 — Interviewing with a Harmonizer]], [[Chapter 13 — Discoveries and Long-Term Insights]], [[Chapter 14 — Appendix and Reference Framework]]
> Tags: #no-read-yet #book-summary

## 📌 Sinopsis Ejecutiva de la Obra

*Interviewology: The New Science of Interviewing*, escrito por la exdirectora de reclutamiento corporativo y coach ejecutiva Anna Papalia, representa una revolución metodológica en la gestión de talento y la preparación para entrevistas de trabajo. Nacido de la observación directa de miles de candidaturas y respaldado por una investigación psicométrica de campo con más de 10,000 participantes, el libro desarticula el paradigma tradicional de las "respuestas memorizadas" y demuestra que el éxito en las entrevistas depende de la autoconciencia psicológica y el dominio situacional de los estilos de comunicación.

La tesis central de Papalia establece que todas las personas ingresan a un proceso de selección a través de uno de cuatro estilos de entrevista claramente definidos: **Charmer (El Encantador)**, **Challenger (El Desafiante)**, **Examiner (El Examinador)** y **Harmonizer (El Armonizador)**. Ningún estilo es inherentemente superior o defectuoso. Cada perfil posee virtudes distintivas, pero cuando la presión o la falta de autoconciencia aumentan, los candidatos sobreutilizan sus fortalezas hasta convertirlas en debilidades autodestructivas: los Charmers sacrifican sustancia por simpatía; los Challengers resultan confrontativos; los Examiners caen en la parálisis por exceso de detalle técnico; y los Harmonizers invisibilizan sus logros individuales en favor del equipo.

Para los gerentes de contratación y reclutadores, *Interviewology* expone cómo los sesgos no examinados —como la búsqueda instintiva del "click" personal o la preferencia por candidatos que duplican el propio estilo del entrevistador— destruyen la equidad y eliminan al 75% del mercado de talento. La obra proporciona un marco de trabajo integrado con herramientas prácticas (como la Pirámide Invertida, el Encuadre Constructivo y la Fórmula de Crédito Dual) que permiten tanto a los candidatos como a las organizaciones transformar las entrevistas en conversaciones objetivas, transparentes y de alto rendimiento.

## 🗺️ Mapa de Arquitectura del Libro

```mermaid
mindmap
  root((Interviewology: Anna Papalia))
    Parte I: Fundamentos e Historia
      [[Chapter 00 — Front Matter and Foundations]]
      [[Chapter 01 — An Interview Can Change Your Life]]
      [[Chapter 02 — How I Discovered the Four Interview Styles]]
      [[Chapter 03 — Why Its Important to Know Your Interview Style]]
      [[Chapter 04 — The Four Interview Styles]]
    Parte II: Los 4 Estilos y sus Dinámicas
      Estilo Charmer
        [[Chapter 05 — The Charmer]]
        [[Chapter 06 — Interviewing with a Charmer]]
      Estilo Challenger
        [[Chapter 07 — The Challenger]]
        [[Chapter 08 — Interviewing with a Challenger]]
      Estilo Examiner
        [[Chapter 09 — The Examiner]]
        [[Chapter 10 — Interviewing with an Examiner]]
      Estilo Harmonizer
        [[Chapter 11 — The Harmonizer]]
        [[Chapter 12 — Interviewing with a Harmonizer]]
    Parte III: Aplicación y Apéndice
      [[Chapter 13 — Discoveries and Long-Term Insights]]
      [[Chapter 14 — Appendix and Reference Framework]]
```

## 📚 Índice de Capítulos

| Capítulo | Título | Conceptos Clave | Enlace |
| :--- | :--- | :--- | :--- |
| **Cap. 00** | Front Matter and Foundations | Paradigma tradicional vs. Autoconciencia | [[Chapter 00 — Front Matter and Foundations]] |
| **Cap. 01** | An Interview Can Change Your Life | Movilidad social, Sesgo del "Click" | [[Chapter 01 — An Interview Can Change Your Life]] |
| **Cap. 02** | How I Discovered the Four Interview Styles | Inteligencias Múltiples, Psicometría | [[Chapter 02 — How I Discovered the Four Interview Styles]] |
| **Cap. 03** | Why Its Important to Know Your Interview Style | Fortalezas Sobreutilizadas, Sesgos | [[Chapter 03 — Why Its Important to Know Your Interview Style]] |
| **Cap. 04** | The Four Interview Styles | Matriz de Estilos, Taxonomía de Papalia | [[Chapter 04 — The Four Interview Styles]] |
| **Cap. 05** | The Charmer | [[CharmerInterviewStyle]], Rapport | [[Chapter 05 — The Charmer]] |
| **Cap. 06** | Interviewing with a Charmer | Adaptación relacional, Estructura | [[Chapter 06 — Interviewing with a Charmer]] |
| **Cap. 07** | The Challenger | [[ChallengerInterviewStyle]], Autenticidad | [[Chapter 07 — The Challenger]] |
| **Cap. 08** | Interviewing with a Challenger | Firmeza asertiva, Prueba de estrés | [[Chapter 08 — Interviewing with a Challenger]] |
| **Cap. 09** | The Examiner | [[ExaminerInterviewStyle]], Pirámide Invertida | [[Chapter 09 — The Examiner]] |
| **Cap. 10** | Interviewing with an Examiner | Evidencia factual, Métricas STAR | [[Chapter 10 — Interviewing with an Examiner]] |
| **Cap. 11** | The Harmonizer | [[HarmonizerInterviewStyle]], Crédito Dual | [[Chapter 11 — The Harmonizer]] |
| **Cap. 12** | Interviewing with a Harmonizer | Ajuste cultural, Seguridad psicológica | [[Chapter 12 — Interviewing with a Harmonizer]] |
| **Cap. 13** | Discoveries and Long-Term Insights | Equidad en selección, Diversidad real | [[Chapter 13 — Discoveries and Long-Term Insights]] |
| **Cap. 14** | Appendix and Reference Framework | Mitos vs. Verdades, Cheat Sheet | [[Chapter 14 — Appendix and Reference Framework]] |

## 🎴 Flashcards de Estudio

#flashcard
Q: ¿Cuál es la tesis central sostenida por Anna Papalia en Interviewology?
A: Que el éxito en las entrevistas depende de la autoconciencia del estilo propio de comunicación (Charmer, Challenger, Examiner, Harmonizer) y no de memorizar respuestas prefabricadas.

Q: ¿Por qué la sobreutilización de una fortaleza en una entrevista se convierte en una debilidad?
A: Porque bajo la presión del estrés, los candidatos intensifican sus patrones automáticos (ej. el Examiner da exceso de detalle técnico y el Charmer recurre al carisma sin datos), perdiendo efectividad y conexión.

Q: ¿Cuál es el peligro de buscar "hacer click" o empatía personal en una entrevista de trabajo?
A: Es un sesgo inconsciente del entrevistador que evalúa la simpatía e similitud estilística del candidato en lugar de sus competencias técnicas y objetivas para el rol.

Q: ¿Qué diferencia al estilo Charmer del estilo Examiner en su prioridad psicológica?
A: El Charmer quiere gustar y prioriza la química interpersonal, mientras que el Examiner quiere hacerlo bien y prioriza la precisión de los datos y el rigor procesal.

Q: ¿Qué diferencia al estilo Challenger del estilo Harmonizer en su actitud comunicativa?
A: El Challenger prioriza la autenticidad y el debate directo de igual a igual, mientras que el Harmonizer prioriza la adaptación, la lealtad y el consenso del equipo.

Q: ¿Cómo resuelve el candidato Harmonizer el dilema de atribuirse méritos sin sonar egoísta?
A: Mediante la Fórmula de Crédito Dual: reconociendo primero el logro del equipo ("Nosotros") y especificando inmediatamente después su responsabilidad individual directa ("Yo").

Q: ¿Cómo sintetiza el Examiner respuestas técnicas masivas ante entrevistadores ejecutivos?
A: Aplicando la Pirámide Invertida: comenzando con el resultado estratégico cuantificable y profundizando en el detalle métrico solo si se solicita.

## 📖 Glosario Especializado

**Interviewology Framework**: Modelo científico desarrollado por Anna Papalia que clasifica el comportamiento de candidatos y reclutadores en cuatro estilos situacionales (Charmer, Challenger, Examiner, Harmonizer).
**Fortaleza Sobreutilizada (Overused Strength)**: Fenómeno psicológico donde un rasgo positivo de comunicación se intensifica bajo presión hasta convertirse en una limitación destructiva.
**Sesgo de Afinidad Estilística**: Tendencia inconsciente del entrevistador a evaluar positivamente a candidatos que comparten su propio perfil comunicativo.
**Pirámide Invertida de Respuesta**: Metodología de comunicación para perfiles analíticos donde se entrega primero la conclusión ejecutiva y luego los detalles de soporte.
**Fórmula de Crédito Dual**: Estructura de respuesta para perfiles armonizadores que equilibra el reconocimiento del esfuerzo colectivo ("Nosotros") con la precisión del impacto individual ("Yo").
**Encuadre Constructivo**: Táctica de comunicación para perfiles desafiantes que transforma críticas directas en preguntas de indagación estratégica y colaborativa.

## 🔗 Conceptos Relacionados en la Wiki

- [[InterviewologyFramework]]
- [[CharmerInterviewStyle]]
- [[ChallengerInterviewStyle]]
- [[ExaminerInterviewStyle]]
- [[HarmonizerInterviewStyle]]
- [[InterviewBiasAndSelfAwareness]]
"""

with open(MAIN_NOTE_PATH, "w", encoding="utf-8") as f:
    f.write(main_note_content.strip() + "\n")

print("✓ Main Executive Note written successfully!")

# -----------------------------------------------------------------------------
# WIKI CONCEPT NOTES
# -----------------------------------------------------------------------------

wiki_concepts = {
    "InterviewologyFramework.md": """# Interviewology Framework

> **Concepto de Arquitectura de Evaluación Laboral**
> Categoría: [[Anna Papalia — Interviewology The New Science of Interviewing]]
> Tipo: wiki-concept
> Tags: #interviewology #framework #recruiting #management

## Definición
El **Interviewology Framework** es el modelo psicométrico y situacional desarrollado por Anna Papalia que categoriza los comportamientos en entrevistas de trabajo en cuatro estilos fundamentales: **Charmer**, **Challenger**, **Examiner** y **Harmonizer**. A diferencia de los tests tradicionales de personalidad, este marco mide las prioridades psicológicas y las conductas comunicativas bajo la presión específica de una selección de personal.

## Matriz de Estilos de Entrevista

```mermaid
quadrantChart
    title Matriz de Estilos de Interviewology
    x-axis Tareas / Datos --> Personas / Conexión
    y-axis Reservado / Adaptativo --> Expansivo / Directo
    quadrant-1 Charmer
    quadrant-2 Challenger
    quadrant-3 Examiner
    quadrant-4 Harmonizer
```

## Relación de los 4 Estilos
- [[CharmerInterviewStyle]]: Enfoque relacional. Prioridad: Gustar.
- [[ChallengerInterviewStyle]]: Enfoque auténtico/directo. Prioridad: Ser uno mismo.
- [[ExaminerInterviewStyle]]: Enfoque métrico/procesal. Prioridad: Hacerlo bien.
- [[HarmonizerInterviewStyle]]: Enfoque colaborativo. Prioridad: Adaptarse.

## Impacto en la Gestión de Talento
La implementación del marco en organizaciones elimina el [[InterviewBiasAndSelfAwareness]], garantizando que las decisiones de contratación se basen en competencias objetivas y no en preferencias estilísticas del reclutador.
""",

    "CharmerInterviewStyle.md": """# Charmer Interview Style

> **Estilo de Entrevista: El Encantador**
> Categoría: [[Anna Papalia — Interviewology The New Science of Interviewing]]
> Tipo: wiki-concept
> Tags: #charmer #interviewology #communication

## Definición
El **Charmer (El Encantador)** es uno de los cuatro estilos centrales del [[InterviewologyFramework]]. Su prioridad psicológica dominante en la entrevista es **gustar y ser apreciado (*Wants to be liked*)**. Confía en el carisma, la calidez, la narración de historias y la química personal como los factores determinantes para obtener el empleo.

## Características y Conductas
- **Fortalezas**: Extraordinaria capacidad para romper el hielo, construir rapport inmediato, proyectar entusiasmo e inspirar confianza social.
- **Sobreutilización / Riesgo**: Confiar excesivamente en la simpatía y descuidar la preparación técnica. Ante preguntas difíciles, recurre al humor o a anécdotas en lugar de entregar datos factuales.
- **Estrategia de Mitigación**: Aplicar la *Regla de Sustancia Previa*, respaldando el encanto natural con 3 a 5 casos de estudio en formato STAR cargados de datos cuantitativos.

## Relacionados
- [[InterviewologyFramework]]
- [[ExaminerInterviewStyle]]
- [[InterviewBiasAndSelfAwareness]]
""",

    "ChallengerInterviewStyle.md": """# Challenger Interview Style

> **Estilo de Entrevista: El Desafiante**
> Categoría: [[Anna Papalia — Interviewology The New Science of Interviewing]]
> Tipo: wiki-concept
> Tags: #challenger #interviewology #leadership

## Definición
El **Challenger (El Desafiante)** es el perfil del [[InterviewologyFramework]] enfocado en la **autenticidad y el respeto mutuo (*Wants to be themselves*)**. Concibe la entrevista como un debate entre iguales, donde no teme cuestionar premisas, señalar ineficiencias de la empresa y defender sus posturas profesionales.

## Características y Conductas
- **Fortalezas**: Pensamiento crítico avanzado, coraje para cuestionar el *statu quo*, resistencia al pensamiento de grupo (*groupthink*) e inmunidad a la presión.
- **Sobreutilización / Riesgo**: Ser percibido como un candidato conflictivo, arrogante o inflexible cuando su tono crítico no es filtrado emocionalmente.
- **Estrategia de Mitigación**: Implementar el *Encuadre Constructivo*, transformando juicios directos en preguntas estratégicas de indagación colaborativa.

## Relacionados
- [[InterviewologyFramework]]
- [[HarmonizerInterviewStyle]]
- [[InterviewBiasAndSelfAwareness]]
""",

    "ExaminerInterviewStyle.md": """# Examiner Interview Style

> **Estilo de Entrevista: El Examinador**
> Categoría: [[Anna Papalia — Interviewology The New Science of Interviewing]]
> Tipo: wiki-concept
> Tags: #examiner #interviewology #data #precision

## Definición
El **Examiner (El Examinador)** es el perfil más metódico y estructurado del [[InterviewologyFramework]]. Su motor psicológico es **hacerlo bien y ser preciso (*Wants to get it right*)**. Se apoya en la investigación profunda, las métricas cuantitativas y la verdad factual como la única prueba de competencia profesional.

## Características y Conductas
- **Fortalezas**: Rigor métrico insuperable, preparación minuciosa, honestidad intelectual y dominio procesal.
- **Sobreutilización / Riesgo**: Caer en la parálisis por análisis y ofrecer monólogos técnicos desbordantes que aburren a entrevistadores de visión ejecutiva.
- **Estrategia de Mitigación**: Aplicar la *Pirámide Invertida de Respuesta*, entregando primero la conclusión ejecutiva cuantitativa y profundizando en el detalle solo si es solicitado.

## Relacionados
- [[InterviewologyFramework]]
- [[CharmerInterviewStyle]]
- [[InterviewBiasAndSelfAwareness]]
""",

    "HarmonizerInterviewStyle.md": """# Harmonizer Interview Style

> **Estilo de Entrevista: El Armonizador**
> Categoría: [[Anna Papalia — Interviewology The New Science of Interviewing]]
> Tipo: wiki-concept
> Tags: #harmonizer #interviewology #teamwork

## Definición
El **Harmonizer (El Armonizador)** es el estilo orientado al trabajo en equipo y la lealtad dentro del [[InterviewologyFramework]]. Su prioridad central es **adaptarse y colaborar (*Wants to adapt*)**. Es un oyente empático que busca la cohesión del grupo y la integración pacífica en la cultura corporativa.

## Características y Conductas
- **Fortalezas**: Escucha activa superior, resolución pacífica de conflictos, lealtad institucional y alta inteligencia emocional relacional.
- **Sobreutilización / Riesgo**: Aversión a la autopromoción. Usar exclusivamente el pronombre "Nosotros", invisibilizando sus aportes individuales y proyectando falta de iniciativa o liderazgo.
- **Estrategia de Mitigación**: Emplear la *Fórmula de Crédito Dual*, reconociendo el esfuerzo colectivo ("Nosotros") y precisando de inmediato la responsabilidad individual directa ("Yo").

## Relacionados
- [[InterviewologyFramework]]
- [[ChallengerInterviewStyle]]
- [[InterviewBiasAndSelfAwareness]]
""",

    "InterviewBiasAndSelfAwareness.md": """# Interview Bias and Self-Awareness

> **Concepto de Psicología Organizacional**
> Categoría: [[Anna Papalia — Interviewology The New Science of Interviewing]]
> Tipo: wiki-concept
> Tags: #bias #self-awareness #hr #recruiting

## Definición
El **Sesgo en Entrevistas y Autoconciencia** es la dimensión crítica analizada por Anna Papalia que explica cómo las decisiones de contratación se distorsionan cuando reclutadores y candidatos carecen de autoconocimiento sobre sus propios perfiles de comunicación.

## Principales Sesgos en la Selección
1. **Sesgo del "Click" Interpersonal**: Evaluar positivamente la simpatía y el rapport del candidato en lugar de sus competencias técnicas reales.
2. **Sesgo de Afinidad Estilística**: Tendencia del evaluador a favorecer a candidatos que duplican su propio estilo dentro del [[InterviewologyFramework]].
3. **Distorsión por Fortaleza Sobreutilizada**: Descartar a profesionales competentes porque su mecanismo de estrés (ej. exceso de detalle en el Examiner o timidez autopromocional en el Harmonizer) es malinterpretado como incompetencia.

## Mitigación Organizacional
- Implementar cuestionarios de comportamiento estandarizados.
- Capacitar a los gerentes de contratación en autoconciencia de su propio perfil de entrevistador.
- Separar la evaluación del desempeño técnico de la impresión relacional.
"""
}

for filename, content in wiki_concepts.items():
    path = WIKI_ROOT / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✓ Wiki concept written: {filename}")

print("✓ Main Note and Wiki Concepts build complete!")
