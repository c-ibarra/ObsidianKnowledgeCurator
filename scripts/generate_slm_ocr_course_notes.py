#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.config import VAULT_ROOT

COURSE_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/raw/Courses/SLM & OCR Course Intro"
WIKI_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/wiki"
MASTER_PLAN_PATH = COURSE_DIR / "Master Plan — SLM & OCR Course.md"

COURSE_DIR.mkdir(parents=True, exist_ok=True)
WIKI_DIR.mkdir(parents=True, exist_ok=True)

notes = [
    {
        "filename": "The Neural Maze — The SLM & OCR Course Starts Now.md",
        "content": """# The Neural Maze — The SLM & OCR Course Starts Now

> **The Neural Maze — The SLM & OCR Course Starts Now (Why SLMs Are Taking Over Vision)**
> Source: https://theneuralmaze.substack.com/p/the-slm-ocr-course-starts-now-the
> Channel/Author: Miguel Otero Pedrido (The Neural Maze) · Date: June 2026
> Playlist/Series: [[Master Plan — SLM & OCR Course]]
> Type: course-intro
> Processed: 18-08-2026
> Tags: #no-read-yet #course #SLM #OCR #VisionLLM #TheNeuralMaze

![[assets/images/slm-ocr-intro-img-01.png]]

## 📌 Key Takeaways
1. **La Disrupción de los SLMs en Visión y OCR**: Los Modelos de Lenguaje Pequeños (*Small Language Models - SLMs*) y Modelos de Lenguaje y Visión (*VLMs*) de 1B a 7B parámetros (como Florence-2, PaliGemma, Qwen2-VL, Moondream2 y Donut) están reemplazando las arquitecturas de OCR tradicionales fragmentadas (detección + reconocimiento + post-procesamiento de NLP) por modelos unificados *end-to-end*.
2. **Eficiencia y Despliegue en el Edge / On-Premise**: A diferencia de invocar APIs cerradas y costosas como GPT-4V o Claude 3.5 Sonnet para millones de documentos, los SLMs permiten inferencia local ultrarrápida, coste marginal casi nulo y cumplimiento estricto de normativas de privacidad (GDPR, HIPAA).
3. **Curación y Arquitectura del Curso**: El programa cubre el ciclo de vida completo de un ingeniero de IA de sistemas: pipelines de OCR moderno, inferencia optimizada de LLMs/SLMs (vLLM, SGLang, TensorRT-LLM) y orquestación escalable sobre clústeres de Kubernetes con GPUs.

---

## 1. El Cambio de Paradigma: De OCR Tradicional a Modelos de Visión-Lenguaje
Durante décadas, la extracción de texto estructurado de documentos dependía de pipelines en cascada:
1. **Binarización y Limpieza**: Filtros OpenCV y reducción de ruido.
2. **Detección de Texto (Text Detection)**: Modelos como CRAFT o DBNet para encontrar cuadros delimitadores (*bounding boxes*).
3. **Reconocimiento de Texto (Text Recognition)**: CRNN o Tesseract para transcribir caracteres.
4. **Análisis de Layout y NLP**: Modelos como LayoutLM para clasificar campos clave (clave-valor, tablas).

![[assets/images/slm-ocr-intro-img-02.webp]]

Este flujo en cascada acumula errores en cada etapa: si la detección falla por 2 píxeles, el reconocedor transcribe basura y el modelo de NLP no puede recuperar la información.

Los **SLMs de Visión** resuelven esto tratando el documento completo como una imagen de entrada y generando directamente JSON o Markdown estructurado en una sola pasada probabilística.

![[assets/images/slm-ocr-intro-img-03.webp]]

---

## 2. Ventajas Competitivas de los SLMs en Producción

![[assets/images/slm-ocr-intro-img-04.webp]]

| Dimensión | Enfoque Legacy (Tesseract / AWS Textract) | APIs de LLM Comerciales (GPT-4o / Claude) | SLMs Especializados (Florence-2 / Qwen2-VL) |
|---|---|---|---|
| **Estructura y Tablas Complejas** | Pobre; requiere heurísticas rígidas | Excelente comprensión, pero formato inconsistente | Excelente con salida JSON estructurada determinista |
| **Costo por 100k Páginas** | Fijo por llamada / alto volumen | $500 - $2,500 USD (prohibitivo a escala) | ~$5 - $20 USD (costo de cómputo GPU local) |
| **Latencia por Página** | 500ms - 2s | 2s - 8s por llamada de red | 50ms - 250ms con engines como vLLM/TensorRT |
| **Privacidad de Datos** | Varía según proveedor SaaS | Envío de datos a terceros | 100% On-Premise / VPC privada |

![[assets/images/slm-ocr-intro-img-05.webp]]

---

## 3. Hoja de Ruta del Ingeniero de Sistemas de IA (*AI Systems Engineer*)
Para construir un sistema de extracción y procesamiento de documentos a nivel industrial no basta con saber entrenar un modelo; se requiere dominar tres pilares complementarios:

![[assets/images/slm-ocr-intro-img-06.webp]]

1. **Comprensión del Document AI Moderno**: Arquitecturas encoder-decoder, tokenización de parches visuales (ViT) y modelos de última generación ([[The Neural Maze — The Complete Guide to Modern OCR]]).
2. **Optimización Extrema de Inferencia**: PagedAttention, KV-Cache compresión, Continuous Batching y cuantización INT4/FP8 ([[The Neural Maze — The Hands-On Guide to LLM Inference]]).
3. **Orquestación en Kubernetes**: Manejo de controladores de GPU de NVIDIA, autoescalado con KEDA y balanceo de carga para endpoints de alta disponibilidad ([[The Neural Maze — Kubernetes for Production AI Engineers]]).

![[assets/images/slm-ocr-intro-img-07.webp]]
![[assets/images/slm-ocr-intro-img-08.png]]

---

## Flashcards
Q: ¿Cuál es el principal problema de los pipelines de OCR tradicionales frente a los SLMs de visión end-to-end?
A: La propagación y acumulación de errores en cascada (ruido -> detección errónea de bounding box -> reconocimiento defectuoso -> fallo en el parser NLP).

Q: ¿Por qué las empresas prefieren desplegar SLMs locales (1B-7B) para OCR en lugar de APIs de modelos frontera?
A: Por reducción radical de costes a escala (hasta 98% de ahorro), latencias ultrabajas (sub-200ms) y cumplimiento estricto de soberanía y privacidad de datos (on-premise/VPC).

---

## Glossary
**Small Language Model (SLM)**: Modelo de lenguaje de tamaño reducido (típicamente entre 1B y 7B parámetros) optimizado para tareas específicas de alta eficiencia.
**Vision-Language Model (VLM)**: Arquitectura multimodal que proyecta parches de imagen y tokens de texto en un espacio latente común para realizar razonamiento visual y generación de texto.
**End-to-End Document Parsing**: Enfoque donde una red neuronal transforma directamente la imagen de un documento en texto formateado (JSON/Markdown) sin módulos intermedios de segmentación.

---

## Related
- [[Master Plan — SLM & OCR Course]]
- [[The Neural Maze — The Complete Guide to Modern OCR]]
- [[The Neural Maze — The Hands-On Guide to LLM Inference]]
- [[The Neural Maze — Kubernetes for Production AI Engineers]]
- [[Modern OCR & Document AI]]
- [[Small Language Models for Vision (VLM-OCR)]]
"""
    },
    {
        "filename": "The Neural Maze — The Complete Guide to Modern OCR.md",
        "content": """# The Neural Maze — The Complete Guide to Modern OCR

> **The Neural Maze — The Complete Guide to Modern OCR (From Tesseract to Vision-Language Models)**
> Source: https://theneuralmaze.substack.com/p/the-complete-guide-to-modern-ocr
> Channel/Author: Miguel Otero Pedrido (The Neural Maze) · Date: July 2026
> Playlist/Series: [[Master Plan — SLM & OCR Course]]
> Type: article
> Processed: 18-08-2026
> Tags: #no-read-yet #course #OCR #DocumentAI #Florence2 #ColPali #Donut

![[assets/images/modern-ocr-img-01.webp]]

## 📌 Key Takeaways
1. **La Taxonomía de las 3 Eras del OCR**:
   - **Era 1 (Reglas y Detección Clásica)**: Tesseract, binarización Otsu y clasificadores de contornos.
   - **Era 2 (Deep Learning Segmentado & LayoutLM)**: CRAFT, DBNet, CRNN + LayoutLMv3 (OCR multimodal con 2D positional embeddings).
   - **Era 3 (End-to-End Vision-Language Models)**: Donut, Nougat, Florence-2, PaliGemma, Qwen2-VL y ColPali (recuperación visual directa).
2. **Modelos Nativos de Documentos (Doc-VLMs)**: Modelos como **Florence-2** y **Nougat** eliminan el paso de OCR intermedio y leen fórmulas matemáticas, tablas complejas y diagramas directamente desde los píxeles hacia Markdown/LaTeX.
3. **ColPali y Visual Document Retrieval**: Utiliza representaciones multivectoriales de parches de imagen (basadas en ColBERT + PaliGemma) para indexar y buscar documentos por su diseño visual sin requerir extracción de texto previa.

---

## 1. Evolución Histórica de los Sistemas de OCR

![[assets/images/modern-ocr-img-02.png]]

El procesamiento de documentos ha pasado de reconocer caracteres tipográficos aislados a interpretar la semántica espacial completa de un archivo digital o escaneado.

![[assets/images/modern-ocr-img-03.png]]

```mermaid
timeline
    title Evolución del Reconocimiento de Documentos
    Era 1 : 1985-2015 : Tesseract / Heurísticas / Binarización
    Era 2 : 2016-2022 : CRNN + CRAFT + LayoutLM (2D Positional Embeddings)
    Era 3 : 2023-Presente : End-to-End VLMs (Nougat, Florence-2, ColPali)
```

![[assets/images/modern-ocr-img-04.png]]

---

## 2. Arquitectura de LayoutLM y la Era Multimodal Clásica
En la Era 2, el estándar corporativo fue **LayoutLMv1/v2/v3**. Su innovación consistió en incorporar embeddings de posición espacial 2D $(x_0, y_0, x_1, y_1)$ junto con los embeddings visuales del parche y los embeddings de texto del token de OCR.

![[assets/images/modern-ocr-img-05.png]]
![[assets/images/modern-ocr-img-06.png]]

A pesar de su éxito, seguía encadenado a la calidad del motor de OCR subyacente. Si el OCR no leía una palabra o la detectaba en orden erróneo, LayoutLM no podía reconstruir el significado.

![[assets/images/modern-ocr-img-07.png]]
![[assets/images/modern-ocr-img-08.png]]

---

## 3. La Revolución End-to-End: Donut, Nougat y Florence-2

![[assets/images/modern-ocr-img-09.webp]]

### Donut (Document Understanding Transformer)
Elimina el reconocedor de OCR. Utiliza un encoder visual (Swin Transformer) conectado a un decoder de texto autorregresivo (BART) para generar árboles JSON estructurados directamente desde la imagen del documento.

![[assets/images/modern-ocr-img-10.png]]

### Nougat (Neural Optical Understanding for Academic Documents)
Especializado en artículos científicos y libros técnicos. Convierte páginas PDF con ecuaciones complejas, matrices y tablas en código LaTeX y Markdown impecable.

![[assets/images/modern-ocr-img-11.webp]]
![[assets/images/modern-ocr-img-12.png]]

### Florence-2 (Microsoft)
Un modelo fundacional unificado para visión que ejecuta múltiples tareas (captioning, object detection, dense region captioning, OCR en cascada y visual grounding) mediante prompts de tareas (`<OCR>`, `<OCR_WITH_REGION>`, `<CAPTION>`).

![[assets/images/modern-ocr-img-13.png]]
![[assets/images/modern-ocr-img-14.png]]

---

## 4. ColPali: Indexación y Búsqueda Visual Directa (Visual RAG)

![[assets/images/modern-ocr-img-15.jpg]]

**ColPali** cambia radicalmente cómo se implementa RAG sobre documentos:
1. En lugar de extraer texto con OCR, trocearlo y calcular embeddings sobre el texto plano (perdiendo tablas, fuentes, colores y figuras), **ColPali calcula embeddings multivectoriales directamente sobre los parches de imagen de la página completa**.
2. Utiliza la técnica de interacción tardía (*late interaction*) de ColBERT sobre el modelo de visión PaliGemma.
3. Permite buscar términos léxicos y conceptos visuales (como gráficos de barras o firmas) con precisión milimétrica.

![[assets/images/modern-ocr-img-16.jpg]]
![[assets/images/modern-ocr-img-17.png]]

---

## 5. Métricas de Evaluación de OCR Moderno

| Métrica | Definición y Uso | Fórmula / Criterio |
|---|---|---|
| **CER (Character Error Rate)** | Tasa de error a nivel de caracteres (sustituciones, eliminaciones e inserciones). | $\text{CER} = \frac{S + D + I}{N}$ |
| **WER (Word Error Rate)** | Tasa de error a nivel de palabras completas. | $\text{WER} = \frac{S_w + D_w + I_w}{N_w}$ |
| **TED (Tree Edit Distance)** | Distancia de edición entre árboles JSON/XML de salida y el ground truth. | Evalúa jerarquía y precisión de extracción de campos clave |
| **F1 Score en Tablas** | Precisión y recall en la detección de celdas, filas y columnas alineadas. | Evalúa estructura tabular compleja |

---

## Flashcards
Q: ¿Qué innovación introdujo LayoutLM en el procesamiento de documentos?
A: La combinación de embeddings de posición espacial 2D (coordenadas de bounding boxes) junto con embeddings de texto y características visuales.

Q: ¿En qué se diferencia ColPali del pipeline clásico de Document RAG?
A: ColPali no extrae texto mediante OCR; vectoriza directamente los parches de imagen del documento mediante late interaction, preservando layout, gráficos y tablas visuales.

Q: ¿Qué ventaja ofrece Florence-2 en tareas de Document AI?
A: Ejecuta múltiples tareas de visión y OCR mediante un único modelo unificado guiado por tokens de prompt especiales (`<OCR>`, `<OCR_WITH_REGION>`).

---

## Glossary
**Late Interaction**: Técnica de recuperación donde las representaciones multivectoriales de la consulta y del documento interactúan solo al final mediante operadores MaxSim, preservando granularidad fina.
**Swin Transformer**: Red neuronal convolucional/atencional basada en ventanas desplazadas utilizada ampliamente como encoder visual de alta resolución.
**Visual Grounding**: Capacidad de un modelo de visión de vincular una descripción textual con las coordenadas espaciales exactas en la imagen.

---

## Related
- [[Master Plan — SLM & OCR Course]]
- [[The Neural Maze — The SLM & OCR Course Starts Now]]
- [[The Neural Maze — The Hands-On Guide to LLM Inference]]
- [[The Neural Maze — Kubernetes for Production AI Engineers]]
- [[Modern OCR & Document AI]]
- [[Small Language Models for Vision (VLM-OCR)]]
"""
    },
    {
        "filename": "The Neural Maze — The Hands-On Guide to LLM Inference.md",
        "content": """# The Neural Maze — The Hands-On Guide to LLM Inference

> **The Neural Maze — The Hands-On Guide to LLM Inference (Optimizing Throughput, Latency & Memory)**
> Source: https://theneuralmaze.substack.com/p/the-hands-on-guide-to-llm-inference
> Channel/Author: Miguel Otero Pedrido (The Neural Maze) · Date: June 2026
> Playlist/Series: [[Master Plan — SLM & OCR Course]]
> Type: article
> Processed: 18-08-2026
> Tags: #no-read-yet #course #LLMInference #vLLM #PagedAttention #TensorRT #Optimization

![[assets/images/llm-inference-img-01.png]]

## 📌 Key Takeaways
1. **El Cuello de Botella en Inferencia (Memory-Bound vs Compute-Bound)**: La fase de *Prefill* (procesamiento del prompt de entrada) está limitada por la capacidad de cómputo (*compute-bound*), mientras que la fase de *Decodificación* (generación token por token) está limitada por el ancho de banda de memoria de la GPU (*memory bandwidth bound*).
2. **PagedAttention y la Eliminación de la Fragmentación**: [[vLLM]] resuelve el desperdicio de hasta un 80% de VRAM en el KV-Cache aplicando paginación de memoria virtual al estilo de los sistemas operativos, permitiendo compartir memoria y aumentar drásticamente el throughput.
3. **Técnicas de Aceleración Avanzadas**:
   - **Continuous Batching / Iteration-level Scheduling**: Empaquetado dinámico de peticiones sin esperar a que terminen las secuencias más largas.
   - **Speculative Decoding**: Un modelo pequeño (draft) genera secuencias de tokens que un modelo grande valida en paralelo en un solo ciclo de atención.
   - **Cuantización (AWQ, GPTQ, FP8, INT4)**: Reducción del tamaño de los pesos y del KV-Cache para duplicar el rendimiento y reducir el consumo de VRAM.

---

## 1. Fases de la Inferencia: Prefill vs Decode

![[assets/images/llm-inference-img-02.png]]

El ciclo de generación en modelos autorregresivos comprende dos etapas con dinámicas físicas radicalmente distintas:

![[assets/images/llm-inference-img-03.png]]

```mermaid
flowchart LR
    subgraph Prefill["1. Prefill Phase (Prompt Evaluation)"]
        P1[Todos los tokens de entrada procesados en paralelo]
        P2[Compute-Bound: GPU Compute Cores saturados]
        P3[Genera KV-Cache inicial]
    end

    subgraph Decode["2. Decode Phase (Token Generation)"]
        D1[Generación secuencial token por token]
        D2[Memory-Bound: Carga de pesos y KV-Cache desde VRAM a SRAM en cada token]
        D3[Determina la latencia de streaming (Time Between Tokens)]
    end

    Prefill --> Decode
```

![[assets/images/llm-inference-img-04.png]]

---

## 2. El Desafío del KV-Cache y la Revolución de PagedAttention

![[assets/images/llm-inference-img-05.webp]]

Para evitar recalcular las matrices de *Key* y *Value* de los tokens anteriores en cada paso, los motores almacenan el **KV-Cache** en la memoria VRAM de la GPU. Sin embargo, en implementaciones estándar:
- Se debe reservar memoria estática para el tamaño máximo de contexto ($\text{max\_seq\_len}$), provocando fragmentación interna y externa masiva.
- Hasta un **60-80% de la memoria de la GPU** se desperdicia en buffers vacíos.

![[assets/images/llm-inference-img-06.png]]

### PagedAttention (vLLM)
Inspirado en la memoria virtual con tablas de páginas de los sistemas operativos, PagedAttention almacena el KV-Cache en bloques de memoria física no contiguos:
- **Cero Desperdicio**: La memoria se asigna dinámicamente bloque a bloque (ej. bloques de 16 tokens).
- **Compartición de Memoria**: Permite que múltiples peticiones (ej. *parallel sampling* o *beam search*) compartan los bloques del prompt idéntico (*Copy-on-Write*).

![[assets/images/llm-inference-img-07.png]]
![[assets/images/llm-inference-img-08.webp]]

---

## 3. Continuous Batching vs Static Batching

![[assets/images/llm-inference-img-09.png]]

En el batching estático tradicional, todas las peticiones de un batch deben esperar a que la petición más larga termine de generar tokens, dejando los núcleos de cómputo inactivos.

El **Continuous Batching (Orca / vLLM)** opera a nivel de iteración: en cada paso de decodificación, las peticiones finalizadas se expulsan del batch y nuevas peticiones entrantes se incorporan de inmediato, multiplicando el throughput por hasta $5\times - 10\times$.

![[assets/images/llm-inference-img-10.png]]

---

## 4. Speculative Decoding y Cuantización

![[assets/images/llm-inference-img-11.png]]

### Speculative Decoding
- Un modelo ligero y rápido (*Draft Model*, ej. 1B) predice especulativamente los próximos $K$ tokens.
- El modelo principal (*Target Model*, ej. 70B) evalúa los $K$ tokens en paralelo en un único paso de prefill.
- Acelera la generación entre $2\times$ y $3\times$ sin alterar la distribución probabilística de salida.

### Cuantización en Motores de Producción
- **Weight-Only Quantization (AWQ, GPTQ)**: Pesos en INT4/INT8, activaciones en FP16.
- **Weight & Activation Quantization (FP8, INT8 SmoothQuant)**: Permite utilizar núcleos Tensor Cores rápidos de arquitecturas Hopper (H100) y Ada Lovelace.
- **KV-Cache Quantization**: Cuantizar el KV-Cache a FP8 reduce su tamaño a la mitad, permitiendo duplicar el tamaño del batch concurrentemente.

![[assets/images/llm-inference-img-12.webp]]

---

## 5. Comparativa de Motores de Inferencia en Producción

| Motor | Creador / Ecosistema | Fortalezas Clave | Mejor Caso de Uso |
|---|---|---|---|
| **vLLM** | UC Berkeley / Open Source | PagedAttention, Continuous Batching, soporte masivo de modelos, fácil despliegue | Despliegues estándar, alta concurrencia, visión multimodal |
| **TensorRT-LLM** | NVIDIA | Máximo rendimiento en hardware NVIDIA, optimizaciones a nivel de kernel C++ | Rendimiento extremo en clústeres empresariales de GPUs H100/A100 |
| **SGLang** | LMSYS | Optimizado para prompts complejos y flujos con llamadas repetidas a herramientas | Agentes complejos, generación de código estructurado |
| **TGI (Text Generation Inference)** | Hugging Face | Integración con el hub de HF, soporte de FlashAttention, métricas Prometheus | Ecosistema Hugging Face en producción |

---

## Flashcards
Q: ¿Por qué la fase de decodificación en LLMs está limitada por el ancho de banda de memoria (memory bandwidth bound)?
A: Porque en cada token generado es necesario transferir todos los pesos del modelo y el KV-Cache acumulado desde la memoria VRAM hacia la memoria SRAM de los núcleos de cómputo para procesar un único vector.

Q: ¿Cómo elimina PagedAttention el desperdicio de memoria en el KV-Cache?
A: Asigna bloques de memoria física no contiguos en la GPU gestionados por una tabla de páginas virtual, eliminando la necesidad de preasignar buffers para la longitud máxima de secuencia.

Q: ¿Qué es el Continuous Batching (Iteration-level scheduling)?
A: Es la técnica de gestión de lotes donde las peticiones finalizadas se retiran y las nuevas se insertan dinámicamente en cada paso de decodificación individual.

---

## Glossary
**KV-Cache**: Búfer en memoria VRAM que almacena las representaciones clave (*Keys*) y valor (*Values*) de la atención de tokens ya procesados para evitar recomputaciones.
**Time to First Token (TTFT)**: Latencia que transcurre desde que se envía el prompt hasta que el modelo emite el primer token generado (dependiente de la fase de Prefill).
**Time Per Output Token (TPOT)**: Tiempo promedio necesario para generar cada token subsiguiente durante el streaming de la respuesta (dependiente de la fase de Decode).
**Speculative Decoding**: Algoritmo de aceleración que combina un modelo borrador rápido con un modelo objetivo que valida ráfagas de tokens en paralelo.

---

## Related
- [[Master Plan — SLM & OCR Course]]
- [[The Neural Maze — The SLM & OCR Course Starts Now]]
- [[The Neural Maze — The Complete Guide to Modern OCR]]
- [[The Neural Maze — Kubernetes for Production AI Engineers]]
- [[LLM Inference Engine Optimization]]
- [[KV Cache & PagedAttention]]
"""
    },
    {
        "filename": "The Neural Maze — Kubernetes for Production AI Engineers.md",
        "content": """# The Neural Maze — Kubernetes for Production AI Engineers

> **The Neural Maze — Kubernetes for Production AI Engineers (Orchestrating GPUs, vLLM & Triton at Scale)**
> Source: https://theneuralmaze.substack.com/p/kubernetes-for-production-ai-engineers
> Channel/Author: Miguel Otero Pedrido (The Neural Maze) · Date: July 2026
> Playlist/Series: [[Master Plan — SLM & OCR Course]]
> Type: article
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Kubernetes #GPU #vLLM #Triton #DevOps #MLOps

![[assets/images/k8s-ai-eng-img-01.png]]

## 📌 Key Takeaways
1. **La Infraestructura Detrás de los Modelos**: En producción, un modelo de lenguaje o de OCR no vive en un script de Python aislado; requiere orquestación sobre clústeres de **Kubernetes (K8s)** con soporte nativo de hardware acelerador (NVIDIA GPU Operator), almacenamiento persistente para pesos de modelos y balanceo de carga L7.
2. **Componentes Nucleares de K8s para IA**:
   - **NVIDIA GPU Operator**: Automatiza el aprovisionamiento de drivers NVIDIA, Container Toolkit y Kubernetes Device Plugin.
   - **KEDA (Kubernetes Event-driven Autoscaling)**: Autoescala pods basándose en métricas de inferencia reales (ej. tamaño de la cola de peticiones en vLLM o latencia TTFT) en lugar de métricas engañosas de CPU/Memoria.
   - **Init Containers y Almacenamiento Compartido**: Descarga eficiente de pesos de modelos desde Hugging Face / S3 hacia volúmenes compartidos (NFS, Ceph o PVCs NVMe locales) para arranques instantáneos de pods.
3. **Patrón de Despliegue de Servidores de Inferencia**: Empaquetado y ejecución de motores como **vLLM** y **Triton Inference Server** con sondas de salud (*readiness/liveness probes*) adaptadas al tiempo de carga del modelo en VRAM.

---

## 1. Por Qué los Ingenieros de IA Deben Dominar Kubernetes

![[assets/images/k8s-ai-eng-img-02.png]]

El paso de prototipos a producción expone problemas críticos de infraestructura:
- **Coste Ocioso de GPUs**: Dejar GPUs dedicadas encendidas sin tráfico genera costes masivos.
- **Failover y Auto-recuperación**: Si un pod sufre un error de memoria fuera de límite (*CUDA OOM*), Kubernetes lo reinicia automáticamente en milisegundos.
- **Distribución de Carga**: Distribución inteligente de peticiones hacia réplicas con capacidad en su KV-Cache.

![[assets/images/k8s-ai-eng-img-03.png]]
![[assets/images/k8s-ai-eng-img-04.png]]

---

## 2. NVIDIA GPU Operator y Gestión de Recursos de GPU

![[assets/images/k8s-ai-eng-img-05.png]]

El **NVIDIA GPU Operator** gestiona el ciclo de vida completo del software de GPU en los nodos del clúster sin requerir instalación manual en el sistema operativo host.

![[assets/images/k8s-ai-eng-img-06.webp]]

### Solicitud de Recursos de GPU en el Manifiesto de K8s
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-qwen-vl-deployment
  namespace: ai-inference
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vllm-qwen-vl
  template:
    metadata:
      labels:
        app: vllm-qwen-vl
    spec:
      containers:
      - name: vllm-server
        image: vllm/vllm-openai:latest
        args:
          - "--model"
          - "Qwen/Qwen2-VL-7B-Instruct"
          - "--gpu-memory-utilization"
          - "0.95"
          - "--max-model-len"
          - "8192"
        resources:
          limits:
            nvidia.com/gpu: "1" # Asignación de 1 GPU física
            memory: "32Gi"
            cpu: "8"
          requests:
            nvidia.com/gpu: "1"
            memory: "16Gi"
            cpu: "4"
        ports:
        - containerPort: 8000
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 10
```

![[assets/images/k8s-ai-eng-img-07.png]]
![[assets/images/k8s-ai-eng-img-08.png]]

---

## 3. Estrategias de Almacenamiento y Carga Rápida de Pesos

![[assets/images/k8s-ai-eng-img-09.png]]

Descargar un modelo de 15 GB desde Hugging Face cada vez que un pod arranca satura la red y genera tiempos de espera inaceptables (*Cold Start* de 5-10 minutos).

![[assets/images/k8s-ai-eng-img-10.png]]

### Solución: PVC Compartido con Init Container
1. Un **PersistentVolumeClaim (PVC)** con acceso `ReadOnlyMany` almacena los pesos pre-descargados.
2. Los pods montan el volumen localmente en `/root/.cache/huggingface` y levantan en menos de 15 segundos.

![[assets/images/k8s-ai-eng-img-11.png]]
![[assets/images/k8s-ai-eng-img-12.png]]

---

## 4. Autoescalado Basado en Eventos de Inferencia con KEDA

![[assets/images/k8s-ai-eng-img-13.png]]

El Horizontal Pod Autoscaler (HPA) estándar de Kubernetes escala por uso de CPU o memoria. En inferencia de IA, **la GPU suele estar al 99% de uso de memoria VRAM todo el tiempo debido a la preasignación del KV-Cache**, haciendo que las métricas estándar sean inútiles.

**KEDA** conecta con los endpoints de métricas de Prometheus exportados por vLLM o Triton y escala según:
- `vllm:num_requests_waiting`: Número de peticiones en cola de espera.
- `vllm:gpu_cache_usage_factor`: Porcentaje real de uso del KV-Cache.

![[assets/images/k8s-ai-eng-img-14.png]]

---

## Flashcards
Q: ¿Por qué el HPA clásico de Kubernetes falla al autoescalar servidores de inferencia LLM como vLLM?
A: Porque vLLM preasigna casi toda la memoria VRAM para el KV-Cache al arrancar, haciendo que la métrica de uso de memoria esté fija en el 90-95% independientemente del tráfico real.

Q: ¿Qué función cumple el NVIDIA GPU Operator en un clúster de Kubernetes?
A: Automatiza la instalación y mantenimiento de los drivers de NVIDIA, el runtime de contenedores y el plugin de dispositivos para exponer GPUs a los pods de forma declarativa.

Q: ¿Cómo se evitan tiempos de cold start prolongados al desplegar pods de inferencia de modelos pesados?
A: Montando volúmenes persistentes compartidos (PVC ReadOnlyMany) con los pesos del modelo pre-descargados y cacheados.

---

## Glossary
**NVIDIA GPU Operator**: Conjunto de controladores y operadores de Kubernetes que gestionan automáticamente los componentes de software de NVIDIA necesarios para ejecutar GPUs.
**KEDA (Kubernetes Event-driven Autoscaling)**: Extensión de Kubernetes que permite escalar cargas de trabajo basándose en métricas de eventos externos (Prometheus, colas SQS, Kafka).
**Cold Start**: Tiempo que transcurre desde que un contenedor es programado en un nodo hasta que está listo para responder tráfico (incluye descarga de imagen, descarga de pesos e inicialización en VRAM).

---

## Related
- [[Master Plan — SLM & OCR Course]]
- [[The Neural Maze — The SLM & OCR Course Starts Now]]
- [[The Neural Maze — The Complete Guide to Modern OCR]]
- [[The Neural Maze — The Hands-On Guide to LLM Inference]]
- [[Kubernetes for AI & GPU Workloads]]
- [[LLM Inference Engine Optimization]]
"""
    }
]

# Wiki concepts
wiki_concepts = [
    {
        "filename": "Modern OCR & Document AI.md",
        "content": """# Modern OCR & Document AI

> **Categoría:** AI Engineering / Computer Vision & NLP
> **Relacionado:** [[Small Language Models for Vision (VLM-OCR)]], [[The Neural Maze — The Complete Guide to Modern OCR]]
> **Tags:** #concept #wiki #OCR #DocumentAI #VisionLLM

## Definición
**Modern OCR & Document AI** comprende la evolución de los sistemas de extracción de información en documentos: desde el reconocimiento óptico de caracteres clásico basado en segmentación heurística hasta los **Modelos de Lenguaje y Visión (VLMs)** que procesan la imagen completa *end-to-end* y extraen texto, tablas y relaciones espaciales en un único paso probabilístico.

## Comparativa de Eras de Document AI

```mermaid
graph TD
    A[Era 1: OCR Heurístico] -->|Tesseract, Binarización| A1[Texto plano sin estructura]
    B[Era 2: Pipelines Segmentados] -->|CRAFT / DBNet + LayoutLM| B1[Bounding boxes + Positional Embeddings]
    C[Era 3: End-to-End Doc-VLMs] -->|Florence-2 / Nougat / ColPali| C1[Markdown / JSON estructurado directo]
```

## Ventajas Clave
1. **Eliminación de la Cascada de Errores**: Sin módulos desconectados de pre-procesamiento, detección y transcripción.
2. **Comprensión Tabular y Visual Nativa**: Comprensión de celdas fusionadas, gráficos, encabezados jerárquicos y firmas.
3. **Salida Estructurada Determinista**: Generación directa de esquemas JSON validados mediante esquemas tipados.

## Relacionado
- [[Small Language Models for Vision (VLM-OCR)]]
- [[The Neural Maze — The Complete Guide to Modern OCR]]
- [[Master Plan — SLM & OCR Course]]
"""
    },
    {
        "filename": "Small Language Models for Vision (VLM-OCR).md",
        "content": """# Small Language Models for Vision (VLM-OCR)

> **Categoría:** AI Engineering / Multimodal Architectures
> **Relacionado:** [[Modern OCR & Document AI]], [[LLM Inference Engine Optimization]]
> **Tags:** #concept #wiki #SLM #VLM #Vision #Florence2 #Donut

## Definición
Los **Small Language Models for Vision (VLM-OCR)** son modelos multimodales compactos (entre 1B y 7B parámetros) entrenados específicamente para interpretar documentos visuales, interfaces gráficas e imágenes de alta densidad textual de forma eficiente.

## Modelos Destacados
- **Florence-2 (Microsoft)**: Modelo fundacional con prompts de tareas unificadas para detección, segmentación y OCR.
- **Nougat (Meta)**: Modelo basado en Donut diseñado para transcripción de papers científicos y fórmulas en LaTeX.
- **PaliGemma (Google) / ColPali**: Arquitectura combinada de SigLIP (visión) y Gemma (lenguaje) para comprensión e indexación multivectorial.
- **Qwen2-VL**: Modelo de visión-lenguaje con soporte de resolución dinámica para documentos ultra-largos.

## Relacionado
- [[Modern OCR & Document AI]]
- [[The Neural Maze — The SLM & OCR Course Starts Now]]
- [[Master Plan — SLM & OCR Course]]
"""
    },
    {
        "filename": "Kubernetes for AI & GPU Workloads.md",
        "content": """# Kubernetes for AI & GPU Workloads

> **Categoría:** MLOps / Infrastructure & Orchestration
> **Relacionado:** [[LLM Inference Engine Optimization]], [[The Neural Maze — Kubernetes for Production AI Engineers]]
> **Tags:** #concept #wiki #Kubernetes #GPU #NVIDIA #vLLM #MLOps

## Definición
**Kubernetes for AI & GPU Workloads** es el conjunto de patrones arquitectónicos, operadores y herramientas para orquestar contenedores que consumen recursos de aceleración gráfica (NVIDIA GPUs, TPUs) para entrenamiento e inferencia escalable de modelos de lenguaje y visión.

## Componentes Críticos del Stack
1. **NVIDIA GPU Operator**: Despliega y gestiona automáticamente los controladores de NVIDIA, el plugin de dispositivos de K8s y las librerías CUDA.
2. **KEDA (Kubernetes Event-driven Autoscaling)**: Autoescala réplicas de pods basándose en métricas de inferencia en tiempo real (tamaño de la cola de peticiones en vLLM) en lugar de uso de CPU/RAM.
3. **PVCs con Model Cache**: Volúmenes compartidos en red de alto rendimiento (NVMe/NFS) para almacenar pesos de modelos y reducir el *Cold Start*.

## Relacionado
- [[LLM Inference Engine Optimization]]
- [[The Neural Maze — Kubernetes for Production AI Engineers]]
- [[Master Plan — SLM & OCR Course]]
"""
    },
    {
        "filename": "LLM Inference Engine Optimization.md",
        "content": """# LLM Inference Engine Optimization

> **Categoría:** AI Engineering / Inference & Serving
> **Relacionado:** [[KV Cache & PagedAttention]], [[Kubernetes for AI & GPU Workloads]]
> **Tags:** #concept #wiki #Inference #vLLM #TensorRT #PagedAttention

## Definición
**LLM Inference Engine Optimization** abarca las técnicas de software y hardware destinadas a maximizar el *throughput* (tokens generados por segundo) y minimizar la latencia (*Time to First Token* y *Time Per Output Token*) durante la ejecución de modelos de lenguaje en producción.

## Pilares de Optimización

```mermaid
flowchart TD
    A[Inference Optimization] --> B[PagedAttention: Zero Memory Waste]
    A --> C[Continuous Batching: Iteration-level scheduling]
    A --> D[Speculative Decoding: Draft + Target Validation]
    A --> E[Quantization: AWQ / FP8 / INT4]
```

## Motores de Inferencia Principales
- **vLLM**: Estándar de la industria para PagedAttention y alta concurrencia.
- **TensorRT-LLM**: Máximo rendimiento en chips NVIDIA H100/A100 con compilación de kernels C++.
- **SGLang**: Optimizado para prompts estructurados y multi-turn agents.

## Relacionado
- [[KV Cache & PagedAttention]]
- [[The Neural Maze — The Hands-On Guide to LLM Inference]]
- [[Master Plan — SLM & OCR Course]]
"""
    },
    {
        "filename": "KV Cache & PagedAttention.md",
        "content": """# KV Cache & PagedAttention

> **Categoría:** AI Engineering / Memory Architectures
> **Relacionado:** [[LLM Inference Engine Optimization]], [[The Neural Maze — The Hands-On Guide to LLM Inference]]
> **Tags:** #concept #wiki #KVCache #PagedAttention #vLLM

## Definición
El **KV Cache** es una estructura en memoria VRAM que almacena las matrices de claves (*Keys*) y valores (*Values*) de los tokens anteriores para evitar recalculaciones durante la generación autorregresiva de LLMs.

**PagedAttention** es el algoritmo introducido por [[vLLM]] que almacena el KV-Cache en bloques físicos no contiguos gestionados mediante tablas de páginas virtuales, reduciendo el desperdicio de VRAM por fragmentación del 80% a menos del 4%.

## Relacionado
- [[LLM Inference Engine Optimization]]
- [[The Neural Maze — The Hands-On Guide to LLM Inference]]
- [[Master Plan — SLM & OCR Course]]
"""
    }
]

master_plan_content = """# Master Plan — SLM & OCR Course

> **Serie:** The AI Systems Engineer Journey (The Neural Maze)
> **Autor:** Miguel Otero Pedrido
> **Vault Path:** `dataScienceKnowledgeBase/AI Engineer/raw/Courses/SLM & OCR Course Intro/`
> **Tags:** #no-read-yet #course #SLM #OCR #VisionLLM #Inference #Kubernetes

---

## 🎯 Descripción del Programa

El **SLM & OCR Course** (publicado por *The Neural Maze*) es una serie técnica avanzada orientada al rol de **AI Systems Engineer**. El curso cubre la transición completa desde los sistemas de OCR heredados hacia **Modelos de Lenguaje Pequeños de Visión (Doc-VLMs/SLMs)**, optimización extrema de inferencia en GPUs (vLLM, PagedAttention, Continuous Batching) y orquestación elástica en clústeres de **Kubernetes**.

---

## 🗺️ Mapa de Módulos y Navegación

### Módulo 1: Introducción y Fundamentos de Visión con SLMs
- [ ] [[The Neural Maze — The SLM & OCR Course Starts Now]] — La revolución de los SLMs en visión, ventajas frente a APIs propietarias y roadmap técnico.

### Módulo 2: Document AI y OCR Moderno
- [ ] [[The Neural Maze — The Complete Guide to Modern OCR]] — De Tesseract a Florence-2, Donut, Nougat y recuperación visual con ColPali.

### Módulo 3: Optimización Extrema de Inferencia
- [ ] [[The Neural Maze — The Hands-On Guide to LLM Inference]] — Prefill vs Decode, KV-Cache, PagedAttention, Continuous Batching, Speculative Decoding y cuantización.

### Módulo 4: Orquestación e Infraestructura en Producción
- [ ] [[The Neural Maze — Kubernetes for Production AI Engineers]] — NVIDIA GPU Operator, KEDA, despliegue de vLLM/Triton, gestión de PVCs y autoescalado por colas.

---

## 🧠 Mapa Conceptual del Sistema

```
THE NEURAL MAZE — SLM & OCR SYSTEMS ENGINEERING
│
├── 1. DOCUMENT AI & MODELOS DE VISIÓN
│   ├── Era 1: OCR Heurístico (Tesseract)
│   ├── Era 2: Pipelines Segmentados (CRAFT + LayoutLMv3)
│   └── Era 3: End-to-End Doc-VLMs ([[Modern OCR & Document AI]])
│       ├── [[Small Language Models for Vision (VLM-OCR)]]
│       ├── Florence-2, Nougat, Donut, Qwen2-VL
│       └── Visual RAG: ColPali (Late Interaction con parches)
│
├── 2. OPTIMIZACIÓN DE INFERENCIA EN PRODUCCIÓN
│   ├── [[LLM Inference Engine Optimization]]
│   ├── [[KV Cache & PagedAttention]] (vLLM)
│   ├── Continuous Batching / Iteration-level scheduling
│   ├── Speculative Decoding (Draft Model + Target Validation)
│   └── Cuantización: AWQ, FP8, INT4
│
└── 3. ORQUESTACIÓN EN KUBERNETES
    ├── [[Kubernetes for AI & GPU Workloads]]
    ├── NVIDIA GPU Operator (Drivers, Container Toolkit, Device Plugin)
    ├── KEDA: Autoescalado por métricas de inferencia (vLLM queue)
    └── Model Storage: PVCs Compartidos & Zero-Cold-Start
```

---

## 🛠️ Stack Tecnológico Dominado

| Capa / Dominio | Tecnologías Principales |
|---|---|
| **Modelos de Visión & OCR** | Florence-2, Nougat, Donut, Qwen2-VL, PaliGemma, ColPali |
| **Motores de Inferencia** | [[vLLM]], TensorRT-LLM, SGLang, Triton Inference Server |
| **Optimización de Memoria** | PagedAttention, KV-Cache FP8, AWQ, Speculative Decoding |
| **Infraestructura & MLOps** | [[Kubernetes]], NVIDIA GPU Operator, KEDA, Prometheus, Docker |

---

## 🔗 Relaciones con Otras Series del Vault
- [[Master Plan — AI Agents]] — Arquitecturas de agentes que consumen herramientas de visión y memoria.
- [[The Neural Maze — Building Agent Memory with Knowledge Graphs]] — Memoria temporal con Graphiti y Neo4j.
- [[Master Plan — Learn Spec-Driven Development]] — Especificación y testing riguroso de sistemas de software.
"""

def main():
    print(f"Generating 4 course notes in {COURSE_DIR}...")
    for n in notes:
        target_file = COURSE_DIR / n["filename"]
        target_file.write_text(n["content"].strip() + "\n", encoding="utf-8")
        print(f"Created: {target_file.name}")

    print(f"\nGenerating 5 wiki concepts in {WIKI_DIR}...")
    for w in wiki_concepts:
        target_file = WIKI_DIR / w["filename"]
        target_file.write_text(w["content"].strip() + "\n", encoding="utf-8")
        print(f"Created/Updated Wiki: {target_file.name}")

    print(f"\nWriting Master Plan at {MASTER_PLAN_PATH}...")
    MASTER_PLAN_PATH.write_text(master_plan_content.strip() + "\n", encoding="utf-8")
    print(f"Master Plan successfully created!")

if __name__ == "__main__":
    main()
