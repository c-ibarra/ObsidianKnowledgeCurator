---
name: okc-bookSummary
description: "Convierte libros de no ficción y documentos extensos (PDF, EPUB, DOCX, HTML, RTF, TXT) en Skills estructuradas ejecutables por agentes de IA y notas completas en Obsidian. Extrae e incrusta automáticamente todas las gráficas, imágenes y diagramas originales en el resumen, sintetiza conceptos, anécdotas, metáforas, preguntas clave, análisis crítico, diagramas Mermaid, tarjetas de estudio y recursos validados de YouTube. Elimina archivos temporales al finalizar."
---

# Non-Fiction Book Curator & Synthesizer (okc-bookSummary)

Transforma conocimiento de libros de no ficción en habilidades estructuradas para agentes de IA y las sube **por defecto al Vault de Obsidian** (`VAULT_ROOT`), preservando la totalidad del contenido visual, imágenes y diagramas.

---

## 🎯 Reglas Principales de Ejecución

1. **Subida por Defecto a Obsidian (`VAULT_ROOT`)**: Todo contenido procesado (nota principal del libro, notas de cada capítulo, imágenes en `assets/images/`, tarjetas `#flashcard`, glosario, conceptos en `wiki/` y actualización del `Master Plan`) **DEBE ser escrito únicamente y por defecto en el Vault de Obsidian** (`VAULT_ROOT`).
2. **Sin Skills Persistentes por Libro**: Las carpetas de skills específicas por libro (p. ej. `.agents/skills/<slug-del-libro>/`) son exclusivamente borradores temporales de trabajo. NO deben persistirse en `.agents/skills/`; todo el conocimiento vive únicamente en el Vault.
3. **Diagramas e Imágenes Obligatorios**: Se deben incrustar las imágenes/figuras extraídas en `assets/images/` del Vault y reconstruir mapas conceptuales, flujos de trabajo y arquitecturas usando **diagramas nativos Mermaid.js** en cada capítulo.
4. **Integración con la Infraestructura**: Cada libro debe vincularse al Master Plan correspondiente, enriquecer o crear notas conceptuales en `wiki/`, y mantener la coherencia del grafo del vault (`knowledge-link`).
5. **Limpieza Automática de Archivos Temporales**: Al finalizar el proceso, **TODOS los archivos de trabajo temporales en `temp/`** (`fetched_book_data.json`, `fetched_book_data.txt`, scripts temporales y carpetas de borrador de la skill) DEBEN ser eliminados automáticamente.

---

## 🎯 Estructura Generada Directamente en Obsidian (`VAULT_ROOT`)

Cada libro procesado generará la siguiente arquitectura de notas y recursos únicamente dentro del Vault de Obsidian:

```
VAULT_ROOT/dataScienceKnowledgeBase/AI Engineer/raw/Books/
├── <Autor> — <Título del Libro>.md       # Resumen principal, flashcards, glosario y recursos
└── <Autor> — <Título del Libro>/
    ├── Chapter 01 — <Título>.md          # Capítulo detallado (900-1500 palabras resum. enriquecido, Mermaid)
    ├── Chapter 02 — <Título>.md
    └── ...
```

---

## 📋 Estructura y Extensión de Cada Capítulo (`chapters/chXX_<titulo>.md`)

> [!IMPORTANT]
> **REGLA DE EXTENSIÓN (SECCIÓN 3: 900–1,500 PALABRAS | TOTAL CAPÍTULO: 1,600–2,650 PALABRAS)**:
> - **Sección 3 (Desarrollo del Resumen Enriquecido)**: DEBE tener una extensión de **900 a 1,500 palabras** para desarrollar a profundidad cada concepto, metáfora, anécdota y diagrama.
> - **Extensión Total Acumulada**: La nota completa del capítulo DEBE sumar **entre 1,600 y 2,650 palabras** al integrar las 5 secciones obligatorias.
> - **Consolidación de Secciones Breves**: Secciones cortas en el libro original (Prefacio, Apéndices, Introducción breve de < 5 páginas) deben ser agrupadas en un capítulo consolidado (p. ej. `Chapter 00 — Front Matter y Apéndice`) para alcanzar el umbral mínimo de 1,600 palabras totales.

Cada capítulo procesado debe contener rigurosamente las siguientes 5 secciones:

### 1. Introducción (200–350 palabras)
Contexto del capítulo, objetivo principal, autor y relevancia dentro del tema central del libro.

### 2. Preguntas Clave (5–7 preguntas, ~100–150 palabras)
Formular las preguntas fundamentales que el lector podrá responder tras estudiar el capítulo.

### 3. Desarrollo del Resumen Enriquecido (900–1,500 palabras, con Imágenes y Diagramas por Defecto)
Desglose conceptual en subsecciones lógicas. Para cada concepto clave:
- Explicación concisa y objetiva.
- **Inclusión Obligatoria de Contenido Visual Original**:
  - **Gráficas, Tablas e Ilustraciones**: Cualquier imagen, figura o gráfica del libro original debe guardarse en `assets/images/<slug>-fig-<num>-<descripcion>.png` e incrustarse **por defecto** en la subsección correspondiente mediante la sintaxis:
    `![[assets/images/<slug>-fig-<num>-<descripcion>.png]]`
    *Pie de figura*: Explicación clara de lo que ilustra el diagrama o gráfica.
- **Anécdotas y Metáforas Inline**: Se deben destacar visualmente en el flujo del texto mediante callouts nativos de Obsidian:
  > [!example] Metáfora: <Título>
  > Descripción de la metáfora y su aplicación práctica.

  > [!quote] Historia Real / Anécdota: <Título>
  > Hecho real o experiencia relatada por el autor y la lección aprendida.

- **Mapa Mental y Diagramas Reconstruidos en Mermaid.js**: Además de las imágenes originales, incluir diagramas conceptuales interactivos nativos en Mermaid:
  ```mermaid
  mindmap
    root((Tema Central))
      Concepto A
        Detalle A1
        Detalle A2
      Concepto B
        Ejemplo B1
  ```

### 4. Análisis Crítico (200–300 palabras)
Evaluación de la solidez de los argumentos, posibles sesgos, limitaciones y comparación breve con otras perspectivas del campo.

### 5. Conclusión (200–350 palabras)
Síntesis de los puntos principales, implicaciones prácticas y direcciones para la aplicación en proyectos reales.

---

## 🎴 Flashcards de Estudio (`flashcards.md`)

Crear 15+ tarjetas con la etiqueta `#flashcard` en formato dual Spaced Repetition (Obsidian / Anki):

```markdown
# Flashcards de Estudio — [[Nombre del Libro]]

#flashcard

Q: ¿Qué es el principio X expuesto por el autor?
A: Definición precisa y contexto de aplicación.

Q: ¿Cuál es la relación causa-efecto entre Y y Z?
A: Explicación de la dinámica.
```

---

## 📚 Glosario y Recursos (`glossary.md` & `resources.md`)

- **`glossary.md`**: Definir entre 5 y 10 términos especializados introducidos o redefinidos en el libro.
- **`resources.md`**: Lista de referencias bibliográficas y **3–5 videos de YouTube validados mediante búsqueda web (`search_web`)** con título, canal y enlace verificado.

---

## 🚀 Flujo de Ejecución e Integración

1. **Ingesta**: Ejecutar `uv run python scripts/fetch_book_data.py --input <ruta-o-url> --slug <slug>`.
2. **Extracción Visual**: Extraer imágenes y diagramas del documento hacia `assets/images/`.
3. **Escritura en Obsidian (Por Defecto)**: Generar las notas del libro y capítulos en `VAULT_ROOT/dataScienceKnowledgeBase/<Categoria>/raw/Books/`.
4. **Construcción de Skill**: Generar la Skill estructurada en `.agents/skills/<slug>/`.
5. **Integración de Infraestructura**: Actualizar el Master Plan de la categoría y crear/actualizar notas en `wiki/`.
6. **Limpieza Automática**: Borrar todos los archivos temporales creados en `temp/`.
7. **Sincronización del Vault**: Ejecutar `uv run python scripts/sync_vault.py`.
