#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.config import VAULT_ROOT

COURSE_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/raw/Courses/AI Dev Tools Zoomcamp"
NOTES_DIR = COURSE_DIR / "course"
WIKI_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/wiki"
MASTER_PLAN_PATH = COURSE_DIR / "Master Plan — AI Dev Tools Zoomcamp.md"

NOTES_DIR.mkdir(parents=True, exist_ok=True)
WIKI_DIR.mkdir(parents=True, exist_ok=True)

# Complete detailed notes dictionary
notes = [
    {
        "filename": "AI Dev Tools Zoomcamp 01 — Course Launch Stream.md",
        "title": "AI Dev Tools Zoomcamp Launch Stream",
        "header_title": "AI Dev Tools Zoomcamp Launch Stream",
        "source": "https://www.youtube.com/watch?v=58pn873XO04",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "content": """# AI Dev Tools Zoomcamp Launch Stream

> **DataTalks.Club — AI Dev Tools Zoomcamp Launch Stream**
> Source: https://www.youtube.com/watch?v=58pn873XO04
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #AI-Dev-Tools

## 📌 Key Takeaways
1. **Enfoque Práctico AI-Native**: El curso está diseñado para transformar a los desarrolladores tradicionales en ingenieros de software asistidos por IA (*AI-native developers*), cubriendo desde editores inteligentes hasta agentes autónomos y pipelines de CI/CD.
2. **Estructura Modular Completa**: Cubre seis módulos nucleares: Fundamentos de herramientas de codificación, Desarrollo end-to-end de aplicaciones completas, Protocolos de contexto ([[Model Context Protocol (MCP)]]), Creación de agentes de codificación personalizados, Orquestación de flujos de trabajo e Integración de automatizaciones inteligentes ([[n8n]]).
3. **Criterios de Evaluación y Capstone**: El aprendizaje se valida mediante tareas semanales prácticas y un proyecto final evaluado por pares (*peer review*), garantizando la entrega de código funcional en producción.

## 1. Filosofía y Objetivos del Curso
El surgimiento de asistentes de código basados en modelos de lenguaje (LLMs) ha redefinido el ciclo de vida del desarrollo de software (SDLC). El objetivo del *AI Dev Tools Zoomcamp* no es enseñar programación básica, sino maximizar el apalancamiento del desarrollador mediante el uso estratégico de herramientas de IA generativa.

```mermaid
flowchart LR
    A[Desarrollo Tradicional] -->|Adopción de IA| B[Desarrollador Aumentado]
    B -->|Context Engineering & MCP| C[Sistemas Multiagente]
    C -->|Producción & CI/CD| D[AI-Native Software Engineering]
```

La premisa central es aprender cuándo usar herramientas de scaffolding rápido (como [[Lovable]]), entornos asistidos (como [[Cursor]] y [[GitHub Copilot]]), protocolos abiertos de contexto ([[Model Context Protocol (MCP)]]) y frameworks de automatización con agentes autónomos.

## 2. Mapa Curricular de Módulos
El contenido del curso se divide en fases progresivas:

| Módulo | Nombre | Enfoque Tecnológico Principal |
|---|---|---|
| **Módulo 1** | Fundamentos y Comparativa de Herramientas | GitHub Codespaces, ChatGPT, Claude, Copilot, Cursor |
| **Módulo 2** | Aplicación End-to-End con IA | React, Lovable, FastAPI, SQLite/PostgreSQL, Docker, Render, CI/CD |
| **Módulo 3** | Model Context Protocol (MCP) | MCP Servers/Clients, Context7, Airflow, VS Code Copilot Extensions |
| **Módulo 4** | Agentes de Código Autónomos | OpenAI Tool Calling, Django Coding Agent, Python Subprocess loop |
| **Módulo 5/6** | Automatización Inteligente con n8n | n8n Workflows, Webhooks, Vector Stores, Memory, AI Nodes |
| **Capstone** | Proyecto Final en Producción | Aplicación completa desplegada con testing y automatización |

## 3. Requisitos de Participación y Entorno
- **Conocimientos Previos**: Familiaridad con Git, línea de comandos de Linux y conceptos básicos de backend (Python) y frontend (HTML/JS).
- **Entorno de Trabajo**: Se recomienda [[GitHub Codespaces]] para estandarizar dependencias y evitar problemas locales de compatibilidad.
- **Herramientas de IA**: Acceso a tiers gratuitos o de bajo coste de modelos de Anthropic (Claude), OpenAI (GPT-4o/o3) o modelos locales via Ollama.

## Flashcards
Q: ¿Cuál es el objetivo principal del curso AI Dev Tools Zoomcamp?
A: Capacitar a desarrolladores en el uso avanzado de herramientas de IA generativa, protocolos de contexto (MCP) y agentes autónomos para construir y desplegar software en producción.

Q: ¿Cuáles son los módulos principales del programa?
A: M1: Herramientas y Comparativa, M2: Aplicación End-to-End, M3: Model Context Protocol (MCP), M4: Agentes de Código Propios, M5/6: Automatización Inteligente con n8n, y Capstone Project.

## Glossary
**AI-Native Development**: Paradigma de ingeniería de software donde la IA generativa participa activamente en el diseño, codificación, testing, containerización y despliegue del sistema.
**Peer Review**: Proceso de evaluación colaborativa donde los estudiantes auditan y califican proyectos de sus compañeros según rúbricas objetivas de producción.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[AI Coding Assistants]]
- [[Model Context Protocol (MCP)]]
- [[LLM Zoomcamp 01 — Introduction to LLMs and RAG]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 02 — Pre-Course Live QA.md",
        "title": "AI Dev Tools Zoomcamp Pre-Course Live QA",
        "header_title": "AI Dev Tools Zoomcamp Pre-Course Live Q&A - Alexey Grigorev",
        "source": "https://www.youtube.com/watch?v=sUwrCnP2iGU",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #AI-Dev-Tools #QA",
        "content": """# AI Dev Tools Zoomcamp Pre-Course Live Q&A

> **DataTalks.Club — AI Dev Tools Zoomcamp Pre-Course Live Q&A - Alexey Grigorev**
> Source: https://www.youtube.com/watch?v=sUwrCnP2iGU
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #AI-Dev-Tools #QA

## 📌 Key Takeaways
1. **Equilibrio entre Asistencia y Comprensión**: Usar herramientas de IA no sustituye la necesidad de comprender la arquitectura del código generado; el desarrollador actúa como arquitecto y revisor crítico.
2. **Selección de Modelos y Costes**: Para la mayoría de los ejercicios es suficiente con tiers gratuitos o créditos básicos de APIs (OpenAI, Claude, Groq o modelos locales vía Ollama).
3. **Manejo del Contexto en Editores**: La calidad del código generado por IA depende directamente de qué archivos y documentación se incluyen en la ventana de contexto del editor.

## 1. Preguntas Frecuentes sobre el Stack y Costes
Durante la sesión previa al inicio del curso, Alexey Grigorev aborda las dudas más comunes sobre la preparación técnica y el hardware requerido:

- **¿Se requiere GPU local?**: No. La mayoría de las herramientas operan como SaaS o utilizan APIs en la nube.
- **¿Es obligatorio pagar suscripciones como Cursor Pro o Copilot?**: No es mandatorio. Se enseñan alternativas de código abierto y configuraciones sobre VS Code tradicional con extensiones gratuitas.
- **¿Qué lenguaje de programación domina el curso?**: Python para el backend y servicios auxiliares; TypeScript/JavaScript y React para el frontend.

## 2. Estrategia de Trabajo con Asistentes de Código
Alexey enfatiza un marco de trabajo en tres fases para no perder el control de la base de código:
1. **Especificación Clara**: Definir contratos de interfaz, modelos de datos y requerimientos antes de pedirle a la IA que implemente funciones.
2. **Generación Incremental**: Construir componentes pequeños y testeables en lugar de pedir aplicaciones monolíticas completas en un solo prompt.
3. **Validación Automática**: Ejecutar suites de tests y linters inmediatamente después de cada generación de código.

## Flashcards
Q: ¿Por qué no es recomendable solicitar una aplicación completa en un solo prompt?
A: Porque aumenta drásticamente la tasa de alucinaciones, código huérfano y dependencias incompatibles. La aproximación óptima es la generación modular e incremental con validación en cada paso.

Q: ¿Qué rol asume el desarrollador al utilizar asistentes de código basados en LLMs?
A: El rol de arquitecto de software, definidor de especificaciones y revisor crítico de calidad y seguridad.

## Glossary
**Context Window (Ventana de Contexto)**: Límite máximo de tokens que un modelo de lenguaje puede procesar simultáneamente, incluyendo prompt del sistema, historial y archivos adjuntos.
**Hallucination (Alucinación)**: Generación de código sintácticamente válido pero que invoca librerías inexistentes o métodos erróneos.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[AI Coding Assistants]]
- [[Context Engineering]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 03 — Configuring Environment with GitHub Codespaces.md",
        "title": "Configuring Environment with GitHub Codespaces",
        "header_title": "Configuring Your Course Environment with GitHub Codespaces",
        "source": "https://www.youtube.com/watch?v=Ky97uuifCZ8",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Codespaces #DevEnvironment",
        "content": """# Configuring Your Course Environment with GitHub Codespaces

> **DataTalks.Club — Configuring Your Course Environment with GitHub Codespaces**
> Source: https://www.youtube.com/watch?v=Ky97uuifCZ8
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Codespaces #DevEnvironment

## 📌 Key Takeaways
1. **Entorno en la Nube Reproducible**: [[GitHub Codespaces]] proporciona una máquina virtual preconfigurada en la nube con Docker, Python, Node.js y extensiones de VS Code listas para usar.
2. **Configuración Declarativa con Dev Containers**: El archivo `.devcontainer/devcontainer.json` permite versionar la configuración del entorno, extensiones y dependencias del sistema.
3. **Port Forwarding Integrado**: Codespaces permite exponer puertos locales (ej. 3000 para React, 8000 para FastAPI) mediante túneles seguros accesibles desde el navegador web.

## 1. Configuración Paso a Paso de Codespaces
El proceso para iniciar un entorno limpio para el curso consta de:
1. Navegar al repositorio del curso en GitHub: `DataTalksClub/ai-dev-tools-zoomcamp`.
2. Crear un nuevo Codespace en la rama principal seleccionando la configuración de máquina predeterminada (2-core o 4-core).
3. Esperar a que el contenedor se inicialice e instale las extensiones recomendadas.

```json
{
  "name": "AI Dev Tools Course Container",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {},
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "GitHub.copilot",
        "esbenp.prettier-vscode"
      ]
    }
  }
}
```

## 2. Gestión de Puertos y Variables de Entorno
- **Port Forwarding**: En la pestaña *Ports* de VS Code, cualquier servicio que escuche en `localhost` se detecta automáticamente y genera una URL HTTPS pública o privada.
- **Secrets de GitHub**: Las claves de API (como `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) deben configurarse en los *Codespace Secrets* del usuario para inyectarse de forma segura en el entorno.

## Flashcards
Q: ¿Qué ventaja ofrece usar Dev Containers en GitHub Codespaces?
A: Garantiza un entorno de desarrollo idéntico para todos los estudiantes, eliminando discrepancias por sistemas operativos y dependencias faltantes.

Q: ¿Cómo se protegen las credenciales de API en Codespaces?
A: Mediante GitHub User Secrets para Codespaces, evitando guardar claves sensibles en archivos dentro del repositorio Git.

## Glossary
**GitHub Codespaces**: Entorno de desarrollo hospedado en la nube respaldado por contenedores Docker e integrado con Visual Studio Code en web o desktop.
**Dev Container**: Estándar de especificación abierta (`devcontainer.json`) para definir entornos de desarrollo completos dentro de contenedores Docker.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[AI Coding Assistants]]
- [[Docker]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 04 — AI Coding Tools Compared.md",
        "title": "AI Coding Tools Compared",
        "header_title": "AI Coding Tools Compared: ChatGPT, Claude, Copilot, Cursor, Lovable and AI Agents",
        "source": "https://www.youtube.com/watch?v=NSMXQk4Axig",
        "date": "July 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #AI-Tools #Benchmark",
        "content": """# AI Coding Tools Compared

> **DataTalks.Club — AI Coding Tools Compared: ChatGPT, Claude, Copilot, Cursor, Lovable and AI Agents**
> Source: https://www.youtube.com/watch?v=NSMXQk4Axig
> Channel/Author: DataTalks.Club · Date: July 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #AI-Tools #Benchmark

## 📌 Key Takeaways
1. **Taxonomía de Herramientas de IA**: Las herramientas se clasifican en cuatro categorías: Asistentes de Chat (ChatGPT, Claude), Completadores en Línea ([[GitHub Copilot]]), Editores Nativos con Indexación Completa ([[Cursor]], [[Windsurf]]) y Generadores de Aplicaciones/Scaffolders ([[Lovable]], Bolt.new, v0).
2. **Indexación de Base de Código (Codebase Indexing)**: Los editores como Cursor destacan por indexar el repositorio completo usando embeddings locales y búsqueda léxica, permitiendo referenciar múltiples archivos con `@file` o `@codebase`.
3. **El Auge de los Agentes de Código Autónomos**: Herramientas como Claude Code, Devin y Roo Code operan en bucles autónomos (Read-Eval-Print-Act) ejecutando comandos de terminal y editando archivos de forma iterativa.

## 1. Comparativa Profunda de Herramientas

| Herramienta | Tipo | Fortalezas | Casos de Uso Ideales |
|---|---|---|---|
| **ChatGPT / Claude Web** | Chat / Razonamiento | Gran capacidad de razonamiento lógico, diseño de arquitecturas | Diseño inicial, algoritmos complejos, análisis de logs |
| **GitHub Copilot** | Autocompletado + Chat | Integración nativa sin fricción, sugerencias multi-línea rápidas | Escribir código boilerplate, tests unitarios rápidos |
| **Cursor / Windsurf** | IDE AI-Native | Indexación global de repositorio, composer multi-archivo, diffs directos | Refactorización de proyectos medianos/grandes, debugging |
| **Lovable / v0 / Bolt** | App Scaffolder | Generación visual instantánea de frontend React/Tailwind con backend mockup | MVPs en minutos, prototipado rápido de UI |
| **Autonomous Coding Agents** | Agentes CLI / IDE | Bucle autónomo: lectura de archivos, ejecución de bash, corrección automática | Tareas de refactorización masiva, solución de issues de GitHub |

## 2. Ventana de Contexto y Gestión de Prompts
El factor limitante en el desarrollo con IA es la gestión del contexto. Los modelos sufren de degradación de atención (*Lost in the Middle*) si se saturan con archivos irrelevantes. La mejor práctica consiste en seleccionar explícitamente los módulos relevantes mediante reglas de proyecto (ej. `.cursorrules`, `.agentrules` o `CLAUDE.md`).

## Flashcards
Q: ¿Cuál es la diferencia fundamental entre un completador de código como Copilot y un IDE AI-native como Cursor?
A: Copilot se enfoca principalmente en autocompletar la línea actual según el archivo abierto, mientras que Cursor indexa todo el repositorio con embeddings y permite editar múltiples archivos simultáneamente.

Q: ¿Cuándo es conveniente utilizar un generador como Lovable en lugar de escribir código desde cero?
A: En la fase inicial de prototipado o MVP para generar una interfaz React interactiva y moderna con componentes UI en pocos segundos.

## Glossary
**Codebase Indexing**: Proceso de vectorizar e indexar archivos de un repositorio para permitir recuperación semántica de fragmentos relevantes durante las consultas al LLM.
**Composer / Multi-file Edit**: Función de los editores modernos de IA que permite al modelo generar y aplicar diffs sincronizados en múltiples archivos simultáneamente.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[AI Coding Assistants]]
- [[Lovable]]
- [[Model Context Protocol (MCP)]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.1 — Implementing an End-to-End AI Application.md",
        "title": "Implementing an End-to-End AI Application (Intro)",
        "header_title": "AI Dev Tools Zoomcamp 2.1 - Implementing an End-to-End AI Application (Intro)",
        "source": "https://www.youtube.com/watch?v=vMNJru1y2Uc",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Architecture #FullStack",
        "content": """# AI Dev Tools Zoomcamp 2.1 - Implementing an End-to-End AI Application (Intro)

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.1 - Implementing an End-to-End AI Application (Intro)**
> Source: https://www.youtube.com/watch?v=vMNJru1y2Uc
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Architecture #FullStack

## 📌 Key Takeaways
1. **Arquitectura Desacoplada Full-Stack**: En este módulo se construye una aplicación completa (el clásico juego Snake enriquecido con tabla de puntuaciones y usuarios) dividida en frontend React, backend FastAPI y base de datos relacional.
2. **Ciclo de Vida de Desarrollo Aumentado por IA**: Cada componente del sistema se implementa utilizando una herramienta de IA especializada: [[Lovable]] para el frontend, agentes y editores para el backend, Docker para containerización y Render para despliegue.
3. **Ingeniería de Software Rigurosa**: A pesar de que el código es generado por IA, se aplican estándares profesionales: tests unitarios en frontend (Vitest), tests de integración en backend (Pytest), linters y pipeline de CI/CD.

## 1. Arquitectura del Sistema
El proyecto se organiza bajo una arquitectura cliente-servidor desacoplada:

```mermaid
graph TD
    Client[Frontend: React + Vite + Tailwind] -->|HTTP REST / JSON| API[Backend: FastAPI / Python]
    API -->|SQLAlchemy ORM| DB[(Database: SQLite / PostgreSQL)]
    TestFE[Vitest / React Testing] --> Client
    TestBE[Pytest / TestClient] --> API
    Docker[Docker & Docker Compose] --> Client
    Docker --> API
    Docker --> DB
```

## 2. Componentes de la Aplicación Snake
- **Frontend**: Interfaz interactiva para el juego Snake, pantalla de Game Over, envío de puntajes y visualización del leaderboard.
- **Backend API**: Endpoints RESTful para registrar usuarios, guardar puntajes (`/api/scores`) y obtener el ranking global (`/api/leaderboard`).
- **Persistencia**: Base de datos SQLite para desarrollo local y PostgreSQL para producción.

## Flashcards
Q: ¿Cuál es el propósito pedagógico del proyecto Snake en el Módulo 2?
A: Demostrar cómo interconectar todas las capas de una aplicación real (frontend, backend, base de datos, testing, containerización y despliegue en la nube) asistido al 100% por herramientas de IA.

Q: ¿Por qué se opta por una arquitectura cliente-servidor desacoplada?
A: Permite generar y probar de manera independiente el frontend en React y el backend en FastAPI con herramientas especializadas antes de la integración.

## Glossary
**Full-Stack Application**: Aplicación de software que comprende tanto la interfaz de usuario (frontend) como la lógica de negocio y datos en el servidor (backend).
**Decoupled Architecture**: Patrón de diseño donde las capas del sistema interactúan únicamente a través de contratos de API bien definidos.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[Lovable]]
- [[FastAPI]]
- [[Docker]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.2 — Creating Frontend with Lovable.md",
        "title": "Creating Frontend with Lovable",
        "header_title": "AI Dev Tools Zoomcamp 2.2 - Creating Frontend with Lovable",
        "source": "https://www.youtube.com/watch?v=F1XJuV1V-BU",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Frontend #Lovable #React",
        "content": """# AI Dev Tools Zoomcamp 2.2 - Creating Frontend with Lovable

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.2 - Creating Frontend with Lovable**
> Source: https://www.youtube.com/watch?v=F1XJuV1V-BU
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Frontend #Lovable #React

## 📌 Key Takeaways
1. **Generación Instantánea de UI con Lovable**: [[Lovable]] permite generar aplicaciones completas de React con Tailwind CSS, componentes shadcn/ui y TypeScript mediante prompts en lenguaje natural.
2. **Iteración Guiada por Prompts**: El flujo de trabajo consiste en describir primero la estructura visual y luego iterar refinando mecánicas específicas (controles del teclado, puntuaciones, modales).
3. **Sincronización Bidireccional con GitHub**: Lovable se conecta directamente con un repositorio de GitHub, enviando commits limpios y estructurados que pueden clonarse para desarrollo local o en Codespaces.

## 1. Creación del Prototipo en Lovable
Alexey demuestra el proceso de prompting en Lovable:
- **Prompt Inicial**: *"Create a classic Snake game with a modern retro dark theme. Include a score counter, a high-score board, start/pause buttons, and arrow key controls."*
- **Refinamiento**: Agregar un diálogo modal al finalizar el juego solicitando el nombre del jugador para guardarlo en la tabla de líderes.

```typescript
// Estructura generada típica en React/TypeScript
interface LeaderboardEntry {
  id: string;
  playerName: string;
  score: number;
  date: string;
}

export const LeaderboardModal = ({ score, onSubmit }: Props) => {
  // Componente React interactivo generado con shadcn/ui
};
```

## 2. Exportación del Código a GitHub
Una vez validado el funcionamiento en la vista previa interactiva de Lovable, se utiliza el botón *Export to GitHub* para transferir el código fuente a un repositorio propio, permitiendo continuar el desarrollo en entornos locales o Codespaces.

## Flashcards
Q: ¿Qué stack técnico genera Lovable por defecto?
A: React, TypeScript, Vite, Tailwind CSS y componentes basados en shadcn/ui / Radix UI.

Q: ¿Cómo se traslada el proyecto de Lovable a un entorno de desarrollo profesional?
A: Mediante la integración nativa de Lovable con GitHub, que realiza un push de todo el código fuente al repositorio del usuario.

## Glossary
**Lovable**: Plataforma de desarrollo de software asistida por IA orientada a la generación rápida y visual de aplicaciones web full-stack en React/TypeScript.
**shadcn/ui**: Colección de componentes de interfaz de usuario reutilizables y accesibles construidos sobre Radix UI y Tailwind CSS.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[Lovable]]
- [[AI Coding Assistants]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.3 — Connecting Antigravity to Codespaces.md",
        "title": "Connecting Antigravity to Codespaces",
        "header_title": "AI Dev Tools Zoomcamp 2.3 - (Optional) Connecting Antigravity to Codespaces",
        "source": "https://www.youtube.com/watch?v=D7vrd8SJENg",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Antigravity #Codespaces",
        "content": """# AI Dev Tools Zoomcamp 2.3 - Connecting Antigravity to Codespaces

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.3 - (Optional) Connecting Antigravity to Codespaces**
> Source: https://www.youtube.com/watch?v=D7vrd8SJENg
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Antigravity #Codespaces

## 📌 Key Takeaways
1. **Flujo de Trabajo Remoto con Antigravity**: Antigravity de Google se puede conectar a entornos remotos como [[GitHub Codespaces]] mediante túneles SSH o extensiones de VS Code, permitiendo que el agente interactúe con el entorno de ejecución en la nube.
2. **Ejecución de Comandos y Edición en Vivo**: El agente tiene la capacidad de inspeccionar el árbol de archivos remoto, ejecutar servidores de desarrollo (`npm run dev`) y verificar errores de consola en tiempo real.
3. **Independencia del Sistema Operativo Local**: Al delegar la ejecución a Codespaces, se eliminan incompatibilidades de Node o dependencias del sistema operativo del usuario.

## 1. Conexión de Antigravity al Entorno Remoto
El procedimiento para habilitar la colaboración del agente en Codespaces involucra:
1. Clonar el repositorio exportado de Lovable dentro del Codespace.
2. Configurar la integración con Antigravity para que reconozca el espacio de trabajo remoto.
3. Permitir que el agente lea el archivo `package.json`, ejecute `npm install` y valide que el frontend se inicialice correctamente en el puerto 8080/5173.

```bash
# Comandos ejecutados dentro del contenedor remoto
git clone https://github.com/<username>/snake-ai-game.git
cd snake-ai-game
npm install
npm run dev -- --host 0.0.0.0
```

## 2. Verificación de la Aplicación en Navegador
Al utilizar el port forwarding de Codespaces, se comprueba que el juego responda fluidamente y que no existan errores de TypeScript en el build inicial.

## Flashcards
Q: ¿Qué beneficio tiene conectar un agente de IA directamente al entorno de Codespaces?
A: Permite al agente ejecutar comandos de build, correr tests y diagnosticar errores directamente en el entorno de ejecución sin requerir intervención manual constante.

Q: ¿Por qué se pasa el parámetro `--host 0.0.0.0` a los servidores de desarrollo en contenedores?
A: Para que el servidor escuche en todas las interfaces de red y el puerto pueda ser reenviado fuera del contenedor.

## Glossary
**SSH Tunneling**: Protocolo de comunicación que encapsula tráfico de red no cifrado dentro de una conexión SSH cifrada.
**Host 0.0.0.0**: Dirección IP que indica a un servicio escuchar conexiones entrantes en todas las interfaces de red disponibles.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[AI Coding Assistants]]
- [[Docker]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.4 — Frontend Testing.md",
        "title": "Frontend Testing",
        "header_title": "AI Dev Tools Zoomcamp 2.4 - (Optional) Frontend Testing",
        "source": "https://www.youtube.com/watch?v=xbsV_RarTUM",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Frontend #Testing #Vitest",
        "content": """# AI Dev Tools Zoomcamp 2.4 - Frontend Testing

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.4 - (Optional) Frontend Testing**
> Source: https://www.youtube.com/watch?v=xbsV_RarTUM
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Frontend #Testing #Vitest

## 📌 Key Takeaways
1. **Calidad y Verificación en Código Generado**: El código generado por herramientas de IA debe acompañarse de tests automatizados para prevenir regresiones y asegurar que la lógica de juego sea correcta.
2. **Configuración de Vitest y React Testing Library**: Se integra [[Vitest]] junto con `jsdom` y `@testing-library/react` para ejecutar tests de componentes y lógica pura en milisegundos.
3. **Generación de Casos de Prueba con Asistentes**: Se utiliza el asistente de IA para identificar casos límite (*edge cases*): colisiones con paredes, colisiones consigo mismo y cálculo correcto de puntajes.

## 1. Configuración de Vitest
Instalación de las dependencias de testing:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

Archivo de configuración `vite.config.ts` o `vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
  },
});
```

## 2. Implementación de Tests Unitarios
Ejemplo de prueba sobre la lógica de movimiento y colisión de la serpiente:
```typescript
import { describe, it, expect } from 'vitest';
import { moveSnake, checkCollision } from '../utils/gameLogic';

describe('Snake Game Logic', () => {
  it('should advance snake head in direction of velocity', () => {
    const initialSnake = [{ x: 10, y: 10 }];
    const direction = { x: 1, y: 0 };
    const nextSnake = moveSnake(initialSnake, direction);
    expect(nextSnake[0]).toEqual({ x: 11, y: 10 });
  });

  it('should detect wall collision correctly', () => {
    const outOfBoundsHead = { x: -1, y: 5 };
    const gridLimit = { width: 20, height: 20 };
    expect(checkCollision(outOfBoundsHead, gridLimit)).toBe(true);
  });
});
```

## Flashcards
Q: ¿Qué ventaja ofrece Vitest frente a Jest en proyectos de Vite?
A: Vitest comparte la misma configuración y pipeline de transformación de Vite, ejecutando los tests de TypeScript de forma nativa y mucho más rápida sin compilación previa.

Q: ¿Por qué es crítico testear la lógica pura (gameLogic) desacoplada de los componentes de React?
A: Porque permite verificar reglas de negocio y casos de borde de forma determinista y sin sobrecarga del DOM virtual.

## Glossary
**Vitest**: Framework de testing unitario ultrarrápido impulsado por Vite con compatibilidad con la API de Jest.
**jsdom**: Implementación en JavaScript puro de los estándares web (DOM y HTML) para entornos de Node.js.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[AI Coding Assistants]]
- [[Lovable]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.5 — Implementing Backend.md",
        "title": "Implementing Backend",
        "header_title": "AI Dev Tools Zoomcamp 2.5 - Implementing Backend",
        "source": "https://www.youtube.com/watch?v=jHVbbw-v_zY",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Backend #FastAPI #Python",
        "content": """# AI Dev Tools Zoomcamp 2.5 - Implementing Backend

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.5 - Implementing Backend**
> Source: https://www.youtube.com/watch?v=jHVbbw-v_zY
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Backend #FastAPI #Python

## 📌 Key Takeaways
1. **Framework Moderno y Tipado con FastAPI**: Se utiliza [[FastAPI]] por su alto rendimiento, validación automática mediante Pydantic y documentación OpenAPI interactiva generada de forma automática (`/docs`).
2. **Estructura de Endpoints para Leaderboard**: Se implementan rutas para registrar nuevas puntuaciones (`POST /scores`) y obtener las mejores puntuaciones ordenadas descendentemente (`GET /leaderboard`).
3. **CORS Middleware**: Es indispensable configurar `CORSMiddleware` en FastAPI para permitir que el frontend servido desde otro puerto/origen pueda realizar peticiones HTTP sin ser bloqueado por el navegador.

## 1. Diseño de Schemas y Endpoints
Estructura inicial del backend con FastAPI y Pydantic:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

app = FastAPI(title="Snake Game API")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScoreCreate(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)
    score: int = Field(..., ge=0)

class ScoreResponse(ScoreCreate):
    id: int
    created_at: datetime

# Mock in-memory database temporal
scores_db = []

@app.post("/api/scores", response_model=ScoreResponse)
def create_score(score_in: ScoreCreate):
    new_entry = {
        "id": len(scores_db) + 1,
        "player_name": score_in.player_name,
        "score": score_in.score,
        "created_at": datetime.utcnow()
    }
    scores_db.append(new_entry)
    return new_entry

@app.get("/api/leaderboard", response_model=List[ScoreResponse])
def get_leaderboard(limit: int = 10):
    sorted_scores = sorted(scores_db, key=lambda x: x["score"], reverse=True)
    return sorted_scores[:limit]
```

## 2. Pruebas Interactivas con Swagger UI
FastAPI genera automáticamente la documentación interactiva en `http://localhost:8000/docs`, permitiendo probar los payloads JSON y respuestas antes de conectar el frontend.

## Flashcards
Q: ¿Para qué sirve el middleware CORS en FastAPI?
A: Para permitir que aplicaciones cliente hospedadas en dominios o puertos diferentes puedan enviar solicitudes HTTP seguras a la API.

Q: ¿Qué función cumple Pydantic en FastAPI?
A: Realiza la validación automática de tipos de datos, serialización y deserialización de payloads JSON y genera el esquema OpenAPI.

## Glossary
**FastAPI**: Framework web moderno y rápido para construir APIs con Python 3.8+ basado en tipos estándar de Python.
**Pydantic**: Librería de validación de datos y gestión de configuraciones basada en anotaciones de tipo de Python.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[FastAPI]]
- [[Python]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.6 — Integrating Frontend and Backend.md",
        "title": "Integrating Frontend and Backend",
        "header_title": "AI Dev Tools Zoomcamp 2.6 - Integrating Frontend and Backend",
        "source": "https://www.youtube.com/watch?v=Y46XU8MYnmY",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Integration #FullStack",
        "content": """# AI Dev Tools Zoomcamp 2.6 - Integrating Frontend and Backend

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.6 - Integrating Frontend and Backend**
> Source: https://www.youtube.com/watch?v=Y46XU8MYnmY
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Integration #FullStack

## 📌 Key Takeaways
1. **Cliente API Centralizado**: En lugar de dispersar llamadas `fetch` por los componentes, se crea un módulo `api.ts` que abstrae las peticiones y gestiona las URLs base.
2. **Variables de Entorno en Vite**: Se utiliza `VITE_API_URL` para configurar dinámicamente el endpoint del backend (`http://localhost:8000` en desarrollo y la URL de Render en producción).
3. **Manejo de Estados Asíncronos**: Implementación de estados de carga (*loading*), éxito y error en la UI al enviar puntuaciones o refrescar el ranking.

## 1. Creación del Servicio de API en Frontend
Código de integración en `src/services/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ScoreData {
  player_name: string;
  score: number;
}

export interface LeaderboardRecord extends ScoreData {
  id: number;
  created_at: string;
}

export const saveScore = async (data: ScoreData): Promise<LeaderboardRecord> => {
  const response = await fetch(`${API_BASE_URL}/api/scores`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Error saving score to backend');
  return response.json();
};

export const fetchLeaderboard = async (): Promise<LeaderboardRecord[]> => {
  const response = await fetch(`${API_BASE_URL}/api/leaderboard?limit=10`);
  if (!response.ok) throw new Error('Error fetching leaderboard');
  return response.json();
};
```

## 2. Conexión con el Componente de Fin de Juego
Al producirse el evento `GameOver`, el componente React invoca `saveScore` y actualiza la lista del leaderboard en pantalla sin recargar la página.

## Flashcards
Q: ¿Por qué en Vite las variables de entorno deben comenzar con el prefijo VITE_?
A: Porque Vite solo expone al código del cliente aquellas variables que explícitamente comiencen con `VITE_` para evitar fugas accidentales de secretos del servidor.

Q: ¿Cómo se manejan los errores de red en el frontend durante la integración?
A: Capturando las excepciones en bloques `try...catch` y mostrando alertas o estados de error en la interfaz sin interrumpir el flujo del juego.

## Glossary
**Environment Variables (Variables de Entorno)**: Valores configurables fuera del código fuente que permiten adaptar el comportamiento de la aplicación según el entorno (dev, staging, prod).
**Async/Await**: Sintaxis moderna de JavaScript para escribir código asíncrono basado en Promesas con estructura secuencial.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[Lovable]]
- [[FastAPI]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.7 — Adding Database for Backend.md",
        "title": "Adding Database for Backend",
        "header_title": "AI Dev Tools Zoomcamp 2.7 - Adding Database for Backend",
        "source": "https://www.youtube.com/watch?v=q8r_ugvQxEE",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Database #SQLAlchemy #PostgreSQL",
        "content": """# AI Dev Tools Zoomcamp 2.7 - Adding Database for Backend

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.7 - Adding Database for Backend**
> Source: https://www.youtube.com/watch?v=q8r_ugvQxEE
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Database #SQLAlchemy #PostgreSQL

## 📌 Key Takeaways
1. **Reemplazo del Mock en Memoria**: La lista temporal de Python se sustituye por una base de datos relacional persistente gestionada mediante **SQLAlchemy ORM**.
2. **Patrón Session & Dependency Injection**: FastAPI utiliza `Depends(get_db)` para inyectar sesiones de base de datos en cada endpoint y asegurar el cierre automático de conexiones.
3. **Portabilidad de Base de Datos**: Gracias a SQLAlchemy, el código opera de manera idéntica sobre SQLite (`sqlite:///./snake.db`) en local o sobre PostgreSQL (`postgresql://...`) en la nube.

## 1. Modelado con SQLAlchemy
Estructura del archivo `database.py` y `models.py`:

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./snake.db")

# Ajuste para Render/PostgreSQL postgres:// vs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ScoreModel(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
```

## 2. Inyección de Dependencia en FastAPI
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/scores")
def create_score(score_in: ScoreCreate, db: Session = Depends(get_db)):
    db_score = ScoreModel(player_name=score_in.player_name, score=score_in.score)
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score
```

## Flashcards
Q: ¿Qué problema soluciona SQLAlchemy ORM frente a escribir SQL nativo?
A: Permite mapear tablas de base de datos a clases de Python, proporcionando tipado seguro, prevención de SQL Injection y portabilidad entre motores de bases de datos.

Q: ¿Por qué es necesario el generador yield en la función get_db()?
A: Porque asegura que la sesión de base de datos se abra para la petición actual y se cierre obligatoriamente en el bloque `finally`, evitando fugas de conexiones (*connection leaks*).

## Glossary
**ORM (Object-Relational Mapping)**: Técnica de programación para convertir datos entre sistemas de tipos incompatibles utilizando programación orientada a objetos.
**SQLAlchemy**: Toolkit de SQL y ORM para Python que proporciona persistencia y abstracción de bases de datos de nivel empresarial.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[FastAPI]]
- [[PostgreSQL]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.7.2 — Integration Tests.md",
        "title": "Integration Tests",
        "header_title": "AI Dev Tools Zoomcamp 2.7.2 - Integration Tests",
        "source": "https://www.youtube.com/watch?v=kfEjwDD5Vv8",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Backend #Testing #Pytest",
        "content": """# AI Dev Tools Zoomcamp 2.7.2 - Integration Tests

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.7.2 - Integration Tests**
> Source: https://www.youtube.com/watch?v=kfEjwDD5Vv8
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Backend #Testing #Pytest

## 📌 Key Takeaways
1. **Verificación de Contrato de API y Base de Datos**: Los tests de integración con **Pytest** y `TestClient` validan el ciclo completo HTTP -> FastAPI -> SQLAlchemy -> SQLite en memoria.
2. **Aislamiento con Fixtures**: Cada test se ejecuta contra una base de datos SQLite en memoria limpia (`sqlite:///:memory:`), garantizando que los tests sean independientes y deterministas.
3. **Validación de Schemas y Respuestas**: Se comprueba tanto el código de estado HTTP (200, 422) como la estructura JSON devuelta y el ordenamiento del leaderboard.

## 1. Configuración de Fixtures en `test_api.py`
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

## 2. Ejecución de Casos de Prueba
```python
def test_create_and_fetch_leaderboard(client):
    # Crear dos puntajes
    client.post("/api/scores", json={"player_name": "Alice", "score": 150})
    client.post("/api/scores", json={"player_name": "Bob", "score": 300})

    # Verificar ranking ordenado
    response = client.get("/api/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["player_name"] == "Bob"
    assert data[0]["score"] == 300
    assert data[1]["player_name"] == "Alice"
```

## Flashcards
Q: ¿Por qué es fundamental usar dependency_overrides en tests de FastAPI?
A: Porque permite sustituir la base de datos de producción o desarrollo por una instancia SQLite temporal en memoria exclusiva para los tests.

Q: ¿Qué valida un test de integración a diferencia de un test unitario?
A: Valida la interacción conjunta entre múltiples componentes (rutas HTTP, validación Pydantic, transacciones de base de datos y serialización de salida).

## Glossary
**TestClient**: Herramienta de testing de FastAPI basada en `httpx` que permite simular peticiones HTTP sin necesidad de levantar un servidor en vivo.
**Pytest Fixture**: Función decorada con `@pytest.fixture` que proporciona datos, recursos o configuraciones previas a los tests.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[FastAPI]]
- [[Python]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.8 — Containerizing Application with Docker-Compose.md",
        "title": "Containerizing Application with Docker-Compose",
        "header_title": "AI Dev Tools Zoomcamp 2.8 - Containerizing the Application and Running it in Docker-Compose",
        "source": "https://www.youtube.com/watch?v=mftbW-QXFRI",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Docker #DockerCompose #DevOps",
        "content": """# AI Dev Tools Zoomcamp 2.8 - Containerizing Application with Docker-Compose

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.8 - Containerizing the Application and Running it in Docker-Compose**
> Source: https://www.youtube.com/watch?v=mftbW-QXFRI
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Docker #DockerCompose #DevOps

## 📌 Key Takeaways
1. **Containerización Multi-Capa**: Empaquetado del frontend (React con servidor Nginx ligero) y backend (FastAPI con Uvicorn) en contenedores Docker independientes.
2. **Orquestación con Docker Compose**: Archivo `docker-compose.yml` que enlaza el frontend, backend y base de datos relacional con redes internas aisladas y volúmenes de datos.
3. **Multi-Stage Builds**: Optimización de las imágenes de Docker reduciendo drásticamente su tamaño al compilar artefactos en una etapa inicial y copiarlos a una imagen base mínima.

## 1. Dockerfile del Frontend (Multi-Stage Build)
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve con Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 2. Dockerfile del Backend
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 3. Orquestación con `docker-compose.yml`
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/snake.db
    volumes:
      - backend_data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  backend_data:
```

## Flashcards
Q: ¿Qué ventaja ofrece un Multi-Stage Build en Docker?
A: Permite utilizar herramientas pesadas (compiladores, Node SDK) en la etapa de compilación y transferir únicamente los binarios/archivos estáticos finales a una imagen de producción muy ligera y segura.

Q: ¿Para qué se utiliza depends_on en Docker Compose?
A: Para definir el orden de inicio de los servicios dependientes (ej. iniciar la base de datos o backend antes de levantar el frontend).

## Glossary
**Docker**: Plataforma de virtualización a nivel de sistema operativo para empaquetar aplicaciones y sus dependencias en contenedores ligeros.
**Docker Compose**: Herramienta para definir y ejecutar aplicaciones multi-contenedor mediante un archivo YAML declarativo.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[Docker]]
- [[FastAPI]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.9 — Deployment to Render Cloud.md",
        "title": "Deployment to Render Cloud",
        "header_title": "AI Dev Tools Zoomcamp 2.9 - Deployment to the Cloud (using Render)",
        "source": "https://www.youtube.com/watch?v=Y7OnXqYs30k",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Cloud #Render #Deployment",
        "content": """# AI Dev Tools Zoomcamp 2.9 - Deployment to Render Cloud

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.9 - Deployment to the Cloud (using Render)**
> Source: https://www.youtube.com/watch?v=Y7OnXqYs30k
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Cloud #Render #Deployment

## 📌 Key Takeaways
1. **Infraestructura como Código (IaC) con Render Blueprint**: Configuración declarativa de toda la infraestructura (Web Service para FastAPI, Static Site para React y Base de Datos PostgreSQL) mediante el archivo `render.yaml`.
2. **Gestión de Secretos y Variables de Entorno**: Inyección segura de credenciales de base de datos (`DATABASE_URL`) y URLs de backend (`VITE_API_URL`) entre los servicios de Render.
3. **Despliegue Continuo Basado en Git**: Cada push a la rama `main` de GitHub activa automáticamente el build y despliegue sin tiempo de inactividad (*zero-downtime deployment*).

## 1. Especificación del Blueprint `render.yaml`
```yaml
services:
  # Backend API Service
  - type: web
    name: snake-backend-api
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: snake-postgres-db
          property: connectionString

  # Frontend Static Site
  - type: web
    name: snake-frontend-app
    env: static
    region: oregon
    plan: free
    buildCommand: "npm install && npm run build"
    staticPublishPath: "./frontend/dist"
    envVars:
      - key: VITE_API_URL
        fromService:
          type: web
          name: snake-backend-api
          property: host

databases:
  - name: snake-postgres-db
    plan: free
    region: oregon
```

## 2. Procedimiento de Lanzamiento en Render
1. Conectar la cuenta de GitHub en el dashboard de Render.
2. Seleccionar *New Blueprint Instance* y vincular el repositorio.
3. Render analiza el archivo `render.yaml`, provisiona la base de datos PostgreSQL, compila el backend FastAPI y despliega el sitio estático con certificados SSL automáticos.

## Flashcards
Q: ¿Qué es un archivo render.yaml Blueprint?
A: Es un archivo declarativo de Infraestructura como Código (IaC) que permite provisionar automáticamente múltiples servicios, bases de datos y variables de entorno en Render.

Q: ¿Por qué es ventajoso desplegar el frontend como Static Site en lugar de Web Service?
A: Porque los sitios estáticos se distribuyen a través de una red CDN global, reducen el consumo de cómputo del servidor y ofrecen tiempos de carga mucho más rápidos.

## Glossary
**Render**: Plataforma en la nube moderna (PaaS) para desplegar aplicaciones web, APIs, bases de datos gestionadas y workers en segundo plano.
**CDN (Content Delivery Network)**: Red de servidores distribuidos geográficamente que entregan contenido web con baja latencia al usuario final.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[FastAPI]]
- [[Docker]]
- [[PostgreSQL]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 2.10 — CICD Pipeline.md",
        "title": "CI/CD Pipeline",
        "header_title": "AI Dev Tools Zoomcamp 2.10 - CI/CD Pipeline",
        "source": "https://www.youtube.com/watch?v=lcmP9YCUmYw",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #CICD #GitHubActions #DevOps",
        "content": """# AI Dev Tools Zoomcamp 2.10 - CI/CD Pipeline

> **DataTalks.Club — AI Dev Tools Zoomcamp 2.10 - CI/CD Pipeline**
> Source: https://www.youtube.com/watch?v=lcmP9YCUmYw
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #CICD #GitHubActions #DevOps

## 📌 Key Takeaways
1. **Automatización de Integración Continua (CI)**: Configuración de **GitHub Actions** para validar automáticamente cada Pull Request ejecutando linters, chequeos de tipos y tests en frontend y backend.
2. **Protección de Ramas y Puertas de Calidad**: Bloqueo de merges en la rama `main` si alguno de los jobs de testing (Vitest o Pytest) falla.
3. **Entrega Continua (CD)**: Activación de webhooks de despliegue en Render únicamente tras la superación exitosa de toda la suite de pruebas.

## 1. Workflow de GitHub Actions (`.github/workflows/ci.yml`)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run Frontend Tests
        run: cd frontend && npm run test -- --run

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
      - name: Run Backend Integration Tests
        run: pytest backend/tests
```

## 2. Beneficios en el Flujo de Desarrollo con IA
Al utilizar agentes de IA para generar o refactorizar código, el pipeline de CI actúa como una red de seguridad inquebrantable, detectando instantáneamente errores de sintaxis, firmas de métodos desactualizadas o fallos lógicos.

## Flashcards
Q: ¿Cuál es la diferencia entre CI (Integración Continua) y CD (Entrega Continua)?
A: CI automatiza la compilación y ejecución de tests con cada cambio de código, mientras que CD automatiza el despliegue del software verificado a los entornos de staging o producción.

Q: ¿Por qué es especialmente importante tener CI cuando se trabaja con asistentes de código de IA?
A: Porque los modelos de lenguaje pueden introducir errores sutiles o dependencias rotas; el pipeline de CI garantiza que solo el código que supera todos los tests llegue a producción.

## Glossary
**GitHub Actions**: Plataforma de automatización y CI/CD integrada directamente en GitHub para orquestar workflows basados en eventos del repositorio.
**Pull Request (PR)**: Propuesta formal de cambios de código en una rama para ser revisada, probada y fusionada en la rama principal.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[Docker]]
- [[FastAPI]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 3.1 — Model Context Protocol Architecture and Servers.md",
        "title": "Model Context Protocol Architecture and Servers",
        "header_title": "Model Context Protocol (MCP): Architecture, Servers, Workflows Automation | Step-by-Step Tutorial",
        "source": "https://www.youtube.com/watch?v=0IhZdcjddo4",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #MCP #ContextEngineering #Architecture",
        "content": """# Model Context Protocol (MCP): Architecture and Servers

> **DataTalks.Club — Model Context Protocol (MCP): Architecture, Servers, Workflows Automation | Step-by-Step Tutorial**
> Source: https://www.youtube.com/watch?v=0IhZdcjddo4
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #MCP #ContextEngineering #Architecture

## 📌 Key Takeaways
1. **El Estándar Abierto de Contexto**: El [[Model Context Protocol (MCP)]], introducido por Anthropic, es un protocolo abierto cliente-servidor basado en JSON-RPC 2.0 que estandariza cómo los LLMs acceden a herramientas (*Tools*), datos (*Resources*) y plantillas (*Prompts*).
2. **Resolución del Problema N x M**: Antes de MCP, cada cliente de IA (Claude Desktop, Cursor, IDEs) necesitaba integraciones propietarias para cada servicio (GitHub, PostgreSQL, Slack). MCP unifica el ecosistema permitiendo que cualquier cliente consuma cualquier servidor MCP.
3. **Primitivas Fundamentales de MCP**: Se definen tres capacidades nucleares:
   - **Tools**: Funciones ejecutables con argumentos estructurados (JSON Schema).
   - **Resources**: Datos de solo lectura contextuales (archivos, esquemas de BD, logs).
   - **Prompts**: Plantillas parametrizadas para guiar interacciones específicas.

## 1. Arquitectura y Topología de MCP
MCP sigue una arquitectura cliente-anfitrión-servidor:

```mermaid
flowchart TD
    subgraph Host["Host Application (Claude Desktop / Cursor / IDE)"]
        Client[MCP Client]
    end

    subgraph Servers["MCP Servers Ecosystem"]
        S1[GitHub MCP Server]
        S2[PostgreSQL MCP Server]
        S3[Context7 MCP Docs]
        S4[Local Filesystem MCP]
    end

    Client <-->|JSON-RPC via Stdio / SSE| S1
    Client <-->|JSON-RPC via Stdio / SSE| S2
    Client <-->|JSON-RPC via Stdio / SSE| S3
    Client <-->|JSON-RPC via Stdio / SSE| S4
```

## 2. Protocolo de Comunicación (Transports)
MCP soporta dos mecanismos de transporte principales:
1. **Stdio (Standard Input/Output)**: Comunicación local por tuberías de procesos, ideal para servidores ejecutados en la misma máquina o contenedor Docker.
2. **SSE (Server-Sent Events) sobre HTTP**: Comunicación para servidores remotos distribuidos en la red.

## 3. Configuración de un Servidor MCP
Ejemplo de configuración en `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/mydb"
      ]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"]
    }
  }
}
```

## Flashcards
Q: ¿Qué problema de integración resuelve el Model Context Protocol (MCP)?
A: Resuelve la proliferación de conectores fragmentados $N \times M$, permitiendo que cualquier cliente de IA interactúe con cualquier fuente de datos o herramienta a través de un estándar único.

Q: ¿Cuáles son las tres primitivas fundamentales expuestas por un servidor MCP?
A: Tools (funciones ejecutables), Resources (datos de lectura estructurados) y Prompts (plantillas parametrizadas).

## Glossary
**Model Context Protocol (MCP)**: Protocolo abierto desarrollado por Anthropic para conectar modelos de lenguaje con herramientas externas y repositorios de datos de forma segura.
**JSON-RPC 2.0**: Protocolo ligero de llamada a procedimiento remoto (RPC) codificado en JSON.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[Model Context Protocol (MCP)]]
- [[Context7 MCP]]
- [[AI Coding Assistants]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 3.2 — MCP Demo Context7 Airflow Copilot.md",
        "title": "MCP Demo Context7 Airflow Copilot",
        "header_title": "AI Dev Tools Zoomcamp 3.2 - MCP Demo (Context7 + Airflow + Copilot)",
        "source": "https://www.youtube.com/watch?v=HYHv_S141CU",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #MCP #Context7 #Airflow #Copilot",
        "content": """# AI Dev Tools Zoomcamp 3.2 - MCP Demo Context7 Airflow Copilot

> **DataTalks.Club — AI Dev Tools Zoomcamp 3.2 - MCP Demo (Context7 + Airflow + Copilot)**
> Source: https://www.youtube.com/watch?v=HYHv_S141CU
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #MCP #Context7 #Airflow #Copilot

## 📌 Key Takeaways
1. **Documentación Actualizada con Context7 MCP**: [[Context7 MCP]] resuelve el problema de conocimiento desactualizado de los LLMs extrayendo documentación técnica oficial en tiempo real directamente al contexto del editor.
2. **Generación Precisa de DAGs de Airflow**: Al conectar Context7 en VS Code, el asistente genera DAGs de Apache Airflow utilizando las últimas versiones de operadores y sintaxis recomendada sin alucinar métodos obsoletos.
3. **Integración con GitHub Copilot Extensions**: Uso de la extensión de MCP en VS Code para invocar herramientas y servidores MCP mediante comandos `@mcp` en el chat del IDE.

## 1. Demostración Práctica en VS Code
Pasos ejecutados durante el taller:
1. Instalar la extensión de soporte MCP en Visual Studio Code.
2. Registrar el servidor de [[Context7 MCP]] para indexar la documentación oficial de Apache Airflow 2.x/3.x.
3. Solicitar al asistente: *"Generate an Apache Airflow DAG with PythonOperator and BashOperator that runs daily, handles retries, and sends failure alerts."*

```python
# DAG generado con precisión gracias a la inyección de documentación via Context7 MCP
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'mcp_curated_etl_pipeline',
    default_args=default_args,
    description='Automated ETL pipeline generated via MCP assisted context',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['mcp', 'etl', 'data-engineering'],
) as dag:

    extract_task = BashOperator(
        task_id='extract_data',
        bash_command='echo "Extracting data from API..."',
    )

    def process_data():
        print("Processing transformed records...")

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=process_data,
    )

    extract_task >> transform_task
```

## 2. Impacto de MCP en la Productividad del Desarrollador
El uso de servidores MCP elimina la fricción de copiar y pegar documentación externa en el prompt, reduciendo errores sintácticos a cero y acelerando la curva de aprendizaje en librerías complejas.

## Flashcards
Q: ¿Qué ventaja aporta Context7 MCP al generar código de librerías en rápida evolución?
A: Proporciona la documentación y firmas de API oficiales y actualizadas al modelo en tiempo real, evitando que genere código basado en versiones antiguas o alucinaciones.

Q: ¿Cómo se comunican los servidores MCP con GitHub Copilot / VS Code?
A: A través de extensiones de VS Code compatibles con el protocolo MCP que exponen herramientas y recursos al contexto del chat del editor.

## Glossary
**Context7 MCP**: Servidor MCP especializado en resolver librerías y consultar documentación oficial actualizada de frameworks de desarrollo.
**Apache Airflow DAG**: Grafo Acíclico Dirigido (*Directed Acyclic Graph*) que define una colección de tareas y sus dependencias de ejecución secuencial o paralela.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[Model Context Protocol (MCP)]]
- [[Context7 MCP]]
- [[AI Coding Assistants]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 4.1 — Build a Django Coding Agent with OpenAI Tools.md",
        "title": "Build a Django Coding Agent with OpenAI Tools",
        "header_title": "Build a Django Coding Agent with OpenAI Tools | Prompt Engineering and Function Calling Tutorial",
        "source": "https://www.youtube.com/watch?v=-XLgk1O421I",
        "date": "August 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #Agent #OpenAI #ToolCalling #Django",
        "content": """# Build a Django Coding Agent with OpenAI Tools

> **DataTalks.Club — Build a Django Coding Agent with OpenAI Tools | Prompt Engineering and Function Calling Tutorial**
> Source: https://www.youtube.com/watch?v=-XLgk1O421I
> Channel/Author: DataTalks.Club · Date: August 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #Agent #OpenAI #ToolCalling #Django

## 📌 Key Takeaways
1. **Arquitectura del Bucle Agéntico (Agentic Loop)**: Construcción desde cero de un agente de codificación autónomo que implementa el ciclo clásico: *Prompt -> LLM decide tool call -> Ejecución en Python -> Retorno de resultado al LLM -> Siguiente iteración*.
2. **Definición de Herramientas Críticas**: El agente dispone de herramientas fundamentales para interactuar con el sistema operativo: `read_file`, `write_file`, `list_directory` y `run_command`.
3. **Scaffolding Autónomo de Django**: A partir de un único prompt en lenguaje natural (*"Create a full Django To-Do application with SQLite, models, views, templates and styling"*), el agente inicializa el proyecto, ejecuta migraciones y escribe las plantillas HTML de forma autónoma.

## 1. Definición de Tool Schemas con OpenAI API
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes content to a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path."},
                    "content": {"type": "string", "description": "Text content of the file."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Executes a shell command in the workspace terminal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run."}
                },
                "required": ["command"]
            }
        }
    }
]
```

## 2. El Bucle de Ejecución del Agente
```python
import subprocess
from openai import OpenAI

client = OpenAI()

def execute_tool(name, args):
    if name == "write_file":
        with open(args["path"], "w", encoding="utf-8") as f:
            f.write(args["content"])
        return f"File {args['path']} written successfully."
    elif name == "run_command":
        res = subprocess.run(args["command"], shell=True, capture_output=True, text=True)
        return f"Exit code: {res.returncode}\nStdout: {res.stdout}\nStderr: {res.stderr}"
    return "Unknown tool"

def run_agent(user_prompt):
    messages = [
        {"role": "system", "content": "You are an autonomous senior Django software engineer. Use tools to create full applications."},
        {"role": "user", "content": user_prompt}
    ]
    
    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        messages.append(msg)
        
        if not msg.tool_calls:
            print("Agent finished task:", msg.content)
            break
            
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            result = execute_tool(fn_name, fn_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
```

## Flashcards
Q: ¿Cuál es el papel del rol 'tool' en la API de Chat Completions de OpenAI?
A: Enviar de vuelta al modelo el resultado de la ejecución de una herramienta (stdout, estado del archivo o error) vinculado al ID de la llamada.

Q: ¿Por qué es fundamental que el agente tenga acceso a run_command?
A: Porque le permite ejecutar migraciones de base de datos (`python manage.py migrate`), instalar librerías (`pip install`) y verificar tests de manera autónoma.

## Glossary
**Function Calling / Tool Calling**: Capacidad de los LLMs para generar llamadas estructuradas en JSON hacia funciones externas predefinidas según las necesidades del usuario.
**Agentic Loop**: Bucle iterativo de retroalimentación donde el modelo evalúa el estado del entorno, ejecuta acciones y ajusta su plan hasta completar el objetivo.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[Autonomous Coding Agents]]
- [[Model Context Protocol (MCP)]]
- [[Python]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 6.1 — n8n Fundamentals to Intelligent Automation Pipelines.md",
        "title": "n8n Fundamentals to Intelligent Automation Pipelines",
        "header_title": "n8n: From Fundamentals to Building Intelligent Automation Pipeline - Moein Foroughi",
        "source": "https://www.youtube.com/watch?v=KR9ApZXsV8g",
        "date": "November 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #n8n #Automation #AIAgents #Workflows",
        "content": """# n8n: Fundamentals to Intelligent Automation Pipelines

> **DataTalks.Club — n8n: From Fundamentals to Building Intelligent Automation Pipeline - Moein Foroughi**
> Source: https://www.youtube.com/watch?v=KR9ApZXsV8g
> Channel/Author: DataTalks.Club · Date: November 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #n8n #Automation #AIAgents #Workflows

## 📌 Key Takeaways
1. **Automatización Low-Code Extensible**: [[n8n]] es una plataforma de automatización de flujos de trabajo basada en nodos de código abierto que combina la facilidad visual del low-code con la potencia de JavaScript/Python y agentes de IA.
2. **Arquitectura del Nodo AI Agent**: n8n incorpora nodos nativos de LangChain que permiten orquestar agentes conversacionales conectándolos visualmente con modelos LLM (OpenAI, Anthropic, Ollama), memoria ([[WindowBufferMemory]]), bases de datos vectoriales y herramientas personalizadas.
3. **Casos de Uso Empresariales**: Automatización de clasificación y respuesta de correos electrónicos, soporte al cliente inteligente, sincronización bidireccional entre CRMs y pipelines de ingestión de datos RAG.

## 1. Nodos Nucleares de n8n para IA
Un pipeline agéntico en n8n se compone de nodos interconectados:

```mermaid
flowchart LR
    Trigger[Webhook / Email Trigger] --> AgentNode[AI Agent Node]
    LLM[Model: OpenAI / Claude] --> AgentNode
    Memory[Window Buffer Memory] --> AgentNode
    Tool1[Custom HTTP Tool] --> AgentNode
    Tool2[Vector Store Qdrant] --> AgentNode
    AgentNode --> Action[Send Slack / DB Update]
```

## 2. Construcción de un Agente con Memoria y Herramientas
Moein Foroughi demuestra la configuración de un agente de atención al cliente:
- **Chat Trigger**: Recibe mensajes del usuario mediante widget web o webhook.
- **AI Agent Node**: Orquesta el razonamiento configurado en modo *Tools Agent*.
- **Memory Node**: Almacena los últimos $N$ intercambios para mantener contexto conversacional.
- **Custom Tool (Calculadora / API CRM)**: Expone endpoints REST como herramientas que el agente invoca cuando requiere consultar datos del cliente.

## Flashcards
Q: ¿Qué diferencia principal existe entre un workflow lineal tradicional en n8n y un flujo con el nodo AI Agent?
A: El workflow tradicional sigue una ruta estática y determinista de pasos, mientras que el AI Agent decide dinámicamente en tiempo de ejecución qué nodos o herramientas invocar según la entrada del usuario.

Q: ¿Cómo se maneja la memoria conversacional en n8n?
A: Mediante sub-nodos especializados de memoria (ej. Window Buffer Memory o Redis Chat Memory) conectados directamente a la ranura de memoria del nodo AI Agent.

## Glossary
**n8n**: Plataforma de automatización de flujos de trabajo extensible, auto-hospedable (*self-hosted*) e integrada con capacidades de IA generativa y agentes.
**Window Buffer Memory**: Mecanismo de persistencia de contexto conversacional que mantiene una ventana deslizante de los últimos $N$ mensajes entre usuario y asistente.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[n8n AI Workflows]]
- [[Autonomous Coding Agents]]
- [[Model Context Protocol (MCP)]]
"""
    },
    {
        "filename": "AI Dev Tools Zoomcamp 6.2 — Setting Up N8N Locally.md",
        "title": "Setting Up N8N Locally",
        "header_title": "AI Dev Tools Zoomcamp 6.2 - Setting Up N8N Locally",
        "source": "https://www.youtube.com/watch?v=vGJKBDlXV-w",
        "date": "December 2025",
        "type": "playlist-item",
        "processed": "18-08-2026",
        "tags": "#no-read-yet #course #n8n #SelfHosting #Docker #DevOps",
        "content": """# AI Dev Tools Zoomcamp 6.2 - Setting Up N8N Locally and in Production

> **DataTalks.Club — AI Dev Tools Zoomcamp 6.2 - Setting Up N8N Locally**
> Source: https://www.youtube.com/watch?v=vGJKBDlXV-w
> Channel/Author: DataTalks.Club · Date: December 2025
> Playlist/Series: [[Master Plan — AI Dev Tools Zoomcamp]]
> Type: playlist-item
> Processed: 18-08-2026
> Tags: #no-read-yet #course #n8n #SelfHosting #Docker #DevOps

## 📌 Key Takeaways
1. **Despliegue Auto-Hospedado con Docker**: Ejecutar [[n8n]] localmente o en un VPS (Ubuntu) proporciona control total sobre los datos, seguridad de claves de API y costos predecibles frente a servicios cloud cerrados.
2. **Configuración de Dominio y SSL con Reverse Proxy**: Para recibir webhooks externos de forma segura (Stripe, GitHub, Telegram), n8n debe ejecutarse detrás de un reverse proxy (como Caddy, Traefik o Nginx) con certificados HTTPS automáticos via Let's Encrypt.
3. **Persistencia de Volúmenes y Variables de Entorno**: Almacenamiento seguro de credenciales, base de datos SQLite/PostgreSQL y configuración de variables críticas (`WEBHOOK_URL`, `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS`).

## 1. Docker Compose para n8n con Caddy Reverse Proxy
Configuración de producción con SSL automático:

```yaml
version: '3.8'

services:
  caddy:
    image: caddy:latest
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config

  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    restart: unless-stopped
    environment:
      - N8N_HOST=n8n.tudominio.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.tudominio.com/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  caddy_data:
  caddy_config:
  n8n_data:
```

Archivo `Caddyfile`:
```
n8n.tudominio.com {
    reverse_proxy n8n:5678
}
```

## 2. Consideraciones de Seguridad
- Desactivar telemetría y registros innecesarios en producción.
- Utilizar autenticación obligatoria y contraseñas robustas para el usuario propietario (*Owner account*).
- Proteger las variables de entorno evitando exponer credenciales en logs del contenedor.

## Flashcards
Q: ¿Por qué es indispensable configurar WEBHOOK_URL con HTTPS en una instancia de n8n?
A: Porque servicios externos como GitHub, Stripe o Telegram requieren endpoints seguros bajo HTTPS para enviar eventos de webhook válidos.

Q: ¿Qué ventaja ofrece el servidor Caddy frente a Nginx en este despliegue?
A: Caddy gestiona y renueva automáticamente los certificados SSL de Let's Encrypt sin requerir configuración adicional de Certbot o cron jobs.

## Glossary
**Self-Hosting (Auto-hospedaje)**: Práctica de ejecutar aplicaciones y servicios en servidores propios o privados en lugar de depender de servicios de terceros.
**Reverse Proxy**: Servidor intermedio que se sitúa frente a los servidores web y redirige las solicitudes de los clientes al servicio correspondiente, gestionando SSL, balanceo y compresión.

## Related
- [[Master Plan — AI Dev Tools Zoomcamp]]
- [[n8n AI Workflows]]
- [[Docker]]
"""
    }
]

# Wiki concepts
wiki_concepts = [
    {
        "filename": "AI Coding Assistants.md",
        "title": "AI Coding Assistants",
        "content": """# AI Coding Assistants

> **Categoría:** AI Engineering / Developer Tooling
> **Relacionado:** [[Model Context Protocol (MCP)]], [[Autonomous Coding Agents]], [[Lovable]]
> **Tags:** #concept #wiki #AI-Dev-Tools

## Definición
Los **AI Coding Assistants** (Asistentes de Código con IA) son herramientas de software impulsadas por Modelos de Lenguaje Grande (LLMs) diseñadas para aumentar la productividad del desarrollador a lo largo de todo el ciclo de vida del desarrollo de software (diseño, autocompletado, refactorización, depuración, testing y documentación).

## Taxonomía de Herramientas

```mermaid
graph TD
    A[AI Coding Assistants] --> B[Inline Autocomplete]
    A --> C[Interactive Chat / Refactor]
    A --> D[AI-Native IDEs]
    A --> E[Visual Scaffolders]
    A --> F[Autonomous CLI Agents]

    B --> B1[GitHub Copilot]
    C --> C1[Claude / ChatGPT]
    D --> D1[Cursor / Windsurf]
    E --> E1[Lovable / v0 / Bolt]
    F --> F1[Claude Code / Devin / Roo Code]
```

## Principios de Ingeniería de Contexto
La efectividad de un asistente de código depende de la **Ingeniería de Contexto** (*Context Engineering*):
1. **Selección Explícita de Archivos**: Evitar saturar el prompt con archivos irrelevantes que diluyan la atención del modelo (*Lost in the Middle*).
2. **Indexación de Repositorio**: Uso de bases de datos vectoriales locales para recuperar fragmentos semánticamente relevantes del codebase.
3. **Reglas de Proyecto**: Archivos de directrices (como `.cursorrules` o `CLAUDE.md`) que establecen convenciones de código, estilos y restricciones arquitectónicas.

## Relacionado
- [[Model Context Protocol (MCP)]]
- [[Autonomous Coding Agents]]
- [[Lovable]]
- [[Master Plan — AI Dev Tools Zoomcamp]]
"""
    },
    {
        "filename": "Model Context Protocol (MCP).md",
        "title": "Model Context Protocol (MCP)",
        "content": """# Model Context Protocol (MCP)

> **Categoría:** AI Engineering / Protocol & Standards
> **Relacionado:** [[Context7 MCP]], [[AI Coding Assistants]], [[Autonomous Coding Agents]]
> **Tags:** #concept #wiki #MCP #Standards

## Definición
El **Model Context Protocol (MCP)** es un estándar abierto cliente-servidor desarrollado originalmente por Anthropic para proporcionar a los modelos de lenguaje un acceso uniforme, seguro y modular a herramientas (*Tools*), fuentes de datos (*Resources*) y plantillas de interacción (*Prompts*).

## Arquitectura y Componentes Nucleares

```mermaid
flowchart LR
    Host[Host Application: IDE / Claude Desktop] --> Client[MCP Client]
    Client <-->|JSON-RPC 2.0| Server1[MCP Server: GitHub]
    Client <-->|JSON-RPC 2.0| Server2[MCP Server: Postgres]
    Client <-->|JSON-RPC 2.0| Server3[MCP Server: Context7]
```

### Primitivas del Protocolo
1. **Tools**: Funciones invocables por el LLM con esquemas JSON de parámetros y validación de tipos.
2. **Resources**: Datos de solo lectura accesibles mediante URIs estructuradas (archivos, logs, esquemas relacionales).
3. **Prompts**: Flujos conversacionales preconfigurados y parametrizables expuestos por el servidor.

### Modos de Transporte
- **Stdio**: Comunicación mediante flujos de entrada y salida estándar en procesos locales.
- **SSE (Server-Sent Events)**: Comunicación a través de HTTP para servidores remotos distribuidos.

## Relacionado
- [[Context7 MCP]]
- [[AI Coding Assistants]]
- [[Autonomous Coding Agents]]
- [[Master Plan — AI Dev Tools Zoomcamp]]
"""
    },
    {
        "filename": "Context7 MCP.md",
        "title": "Context7 MCP",
        "content": """# Context7 MCP

> **Categoría:** AI Engineering / MCP Ecosystem
> **Relacionado:** [[Model Context Protocol (MCP)]], [[AI Coding Assistants]]
> **Tags:** #concept #wiki #MCP #Documentation

## Definición
**Context7 MCP** es un servidor dentro del ecosistema del [[Model Context Protocol (MCP)]] diseñado para resolver dependencias técnicas e inyectar documentación oficial actualizada en tiempo real directamente en la ventana de contexto de los asistentes de código.

## Mecanismo de Funcionamiento
1. El desarrollador o el LLM solicita información sobre una librería (ej. `airflow`, `langchain`, `pydantic`).
2. Context7 resuelve el identificador de la librería y recupera los fragmentos de documentación, firmas de funciones y guías de migración más recientes.
3. El asistente genera código con compatibilidad de versiones garantizada, eliminando alucinaciones por métodos deprecados o sintaxis antigua.

## Relacionado
- [[Model Context Protocol (MCP)]]
- [[AI Coding Assistants]]
- [[Master Plan — AI Dev Tools Zoomcamp]]
"""
    },
    {
        "filename": "Autonomous Coding Agents.md",
        "title": "Autonomous Coding Agents",
        "content": """# Autonomous Coding Agents

> **Categoría:** AI Engineering / Agentic Workflows
> **Relacionado:** [[Model Context Protocol (MCP)]], [[AI Coding Assistants]], [[n8n AI Workflows]]
> **Tags:** #concept #wiki #Agents #ToolCalling

## Definición
Los **Autonomous Coding Agents** (Agentes de Codificación Autónomos) son sistemas de IA capaces de ejecutar ciclos cerrados de razonamiento y acción (*Agentic Loops*) para planificar, escribir, ejecutar, testear y corregir código en un entorno de desarrollo sin requerir intervención humana en cada paso intermedio.

## Ciclo de Vida Agéntico

```mermaid
stateDiagram-v2
    [*] --> Plan: Recibir Objetivo
    Plan --> ExecuteTool: Seleccionar Herramienta
    ExecuteTool --> EvaluateOutput: Ejecutar en Sandbox
    EvaluateOutput --> FixErrors: Si hay error o fallo en tests
    FixErrors --> ExecuteTool
    EvaluateOutput --> Success: Tests aprobados y objetivo cumplido
    Success --> [*]
```

## Herramientas Nucleares de un Agente de Código
- `read_file` / `write_file` / `replace_file_content`: Manipulación de archivos en el workspace.
- `list_dir` / `grep_search`: Exploración y búsqueda de símbolos en la base de código.
- `run_command`: Ejecución de linters, compiladores, suites de testing y migraciones.

## Relacionado
- [[Model Context Protocol (MCP)]]
- [[AI Coding Assistants]]
- [[n8n AI Workflows]]
- [[Master Plan — AI Dev Tools Zoomcamp]]
"""
    },
    {
        "filename": "n8n AI Workflows.md",
        "title": "n8n AI Workflows",
        "content": """# n8n AI Workflows

> **Categoría:** AI Engineering / Low-Code Automation
> **Relacionado:** [[Autonomous Coding Agents]], [[Model Context Protocol (MCP)]]
> **Tags:** #concept #wiki #n8n #Automation

## Definición
**n8n AI Workflows** se refiere a la integración de capacidades agénticas y modelos de lenguaje grande dentro de la plataforma de automatización de código abierto **n8n**, permitiendo crear flujos de trabajo autónomos visualmente.

## Capacidades Principales
- **AI Agent Node**: Nodo orquestador basado en LangChain que decide qué herramientas invocar según la entrada del usuario o evento de webhook.
- **Memoria Integrada**: Persistencia de contexto mediante nodos como `WindowBufferMemory` o almacenes de chat en Redis.
- **RAG Visual**: Conexión nativa con embeddings y bases de datos vectoriales (Qdrant, Pinecone, PGVector).
- **Herramientas Personalizadas**: Conversión instantánea de peticiones HTTP y funciones de código en herramientas (*Tools*) consumibles por el agente.

## Relacionado
- [[Autonomous Coding Agents]]
- [[Model Context Protocol (MCP)]]
- [[Master Plan — AI Dev Tools Zoomcamp]]
"""
    },
    {
        "filename": "Lovable.md",
        "title": "Lovable",
        "content": """# Lovable

> **Categoría:** Developer Tooling / Frontend Generation
> **Relacionado:** [[AI Coding Assistants]], [[Master Plan — AI Dev Tools Zoomcamp]]
> **Tags:** #concept #wiki #Frontend #Lovable #React

## Definición
**Lovable** es una plataforma de desarrollo asistida por IA (*AI Full-Stack App Builder*) orientada a la creación rápida de interfaces de usuario modernas en React, TypeScript, Vite y Tailwind CSS mediante prompts en lenguaje natural.

## Características Clave
- **Vista Previa en Tiempo Real**: Renderizado instantáneo de la aplicación con capacidades de interacción antes de exportar código.
- **Integración con GitHub**: Sincronización bidireccional mediante commits limpios en el repositorio del desarrollador.
- **Ecosistema de Componentes**: Utiliza la librería accesible shadcn/ui y componentes de Radix UI.

## Relacionado
- [[AI Coding Assistants]]
- [[Master Plan — AI Dev Tools Zoomcamp]]
"""
    }
]

# Master Plan Content
master_plan_content = """# Master Plan — AI Dev Tools Zoomcamp

> **Playlist:** [AI Dev Tools Zoomcamp — DataTalksClub](https://youtube.com/playlist?list=PL3MmuxUbc_hLuyafXPyhTdbF4s_uNhc43)
> **GitHub:** https://github.com/DataTalksClub/ai-dev-tools-zoomcamp
> **Canal / Instructor:** DataTalks.Club · Alexey Grigorev · Moein Foroughi
> **Vault:** `AI Engineer/raw/Courses/AI Dev Tools Zoomcamp/course`
> **Tags:** #no-read-yet #course #AI-Dev-Tools #MCP #FullStack #n8n

---

## 🎯 Descripción del Curso

El **AI Dev Tools Zoomcamp** de DataTalks.Club es un programa práctico de formación técnica enfocado en la ingeniería de software nativa de IA (*AI-Native Software Engineering*). El curso cubre desde editores inteligentes y scaffolding de frontend hasta la implementación de protocolos abiertos de contexto ([[Model Context Protocol (MCP)]]), creación de agentes de código autónomos y automatizaciones inteligentes con [[n8n]].

---

## 🗺️ Mapa de Módulos y Navegación

### Módulo 1: Fundamentos y Entorno de Desarrollo
- [ ] [[AI Dev Tools Zoomcamp 01 — Course Launch Stream]] — Visión general, filosofía y roadmap del curso.
- [ ] [[AI Dev Tools Zoomcamp 02 — Pre-Course Live QA]] — Sesión en vivo de preguntas y respuestas, stack técnico y mindset.
- [ ] [[AI Dev Tools Zoomcamp 03 — Configuring Environment with GitHub Codespaces]] — Configuración de entorno reproducible con Dev Containers.
- [ ] [[AI Dev Tools Zoomcamp 04 — AI Coding Tools Compared]] — Comparativa técnica: ChatGPT, Claude, Copilot, Cursor, Lovable y agentes.

### Módulo 2: Implementación de una Aplicación End-to-End con IA
- [ ] [[AI Dev Tools Zoomcamp 2.1 — Implementing an End-to-End AI Application]] — Arquitectura desacoplada del sistema y diseño del proyecto Snake.
- [ ] [[AI Dev Tools Zoomcamp 2.2 — Creating Frontend with Lovable]] — Generación rápida de UI en React/Tailwind/TypeScript con Lovable.
- [ ] [[AI Dev Tools Zoomcamp 2.3 — Connecting Antigravity to Codespaces]] — Conexión y control del entorno remoto de desarrollo.
- [ ] [[AI Dev Tools Zoomcamp 2.4 — Frontend Testing]] — Testing de componentes y lógica pura con Vitest.
- [ ] [[AI Dev Tools Zoomcamp 2.5 — Implementing Backend]] — Creación de la API REST con FastAPI y validación Pydantic.
- [ ] [[AI Dev Tools Zoomcamp 2.6 — Integrating Frontend and Backend]] — Conexión cliente-servidor y gestión de variables de entorno.
- [ ] [[AI Dev Tools Zoomcamp 2.7 — Adding Database for Backend]] — Persistencia relacional con SQLAlchemy ORM y PostgreSQL/SQLite.
- [ ] [[AI Dev Tools Zoomcamp 2.7.2 — Integration Tests]] — Tests de integración con Pytest y SQLite en memoria.
- [ ] [[AI Dev Tools Zoomcamp 2.8 — Containerizing Application with Docker-Compose]] — Multi-stage Dockerfiles y orquestación con Docker Compose.
- [ ] [[AI Dev Tools Zoomcamp 2.9 — Deployment to Render Cloud]] — Infraestructura como Código (IaC) con `render.yaml` y despliegue continuo.
- [ ] [[AI Dev Tools Zoomcamp 2.10 — CICD Pipeline]] — Automatización de tests y quality gates con GitHub Actions.

### Módulo 3: Model Context Protocol (MCP) y Context Engineering
- [ ] [[AI Dev Tools Zoomcamp 3.1 — Model Context Protocol Architecture and Servers]] — Arquitectura, primitivas (Tools, Resources, Prompts) y JSON-RPC.
- [ ] [[AI Dev Tools Zoomcamp 3.2 — MCP Demo Context7 Airflow Copilot]] — Demostración práctica de Context7 MCP y generación de DAGs de Airflow en VS Code.

### Módulo 4: Agentes de Código Autónomos
- [ ] [[AI Dev Tools Zoomcamp 4.1 — Build a Django Coding Agent with OpenAI Tools]] — Bucle agéntico (*Agentic Loop*) con tool calling y ejecución en terminal.

### Módulo 6: Automatización Inteligente con n8n
- [ ] [[AI Dev Tools Zoomcamp 6.1 — n8n Fundamentals to Intelligent Automation Pipelines]] — Fundamentos de n8n, AI Agent Nodes, memoria y vector stores.
- [ ] [[AI Dev Tools Zoomcamp 6.2 — Setting Up N8N Locally]] — Despliegue auto-hospedado con Docker Compose, Caddy Reverse Proxy y SSL.

---

## 🧠 Mapa Conceptual del Curso

```
AI DEV TOOLS ZOOMCAMP — DataTalks.Club
│
├── 1. HERRAMIENTAS & EDITORES AI-NATIVE
│   ├── Editores con indexación: [[Cursor]], Windsurf
│   ├── Autocompletado: [[GitHub Copilot]]
│   ├── Scaffolders: [[Lovable]], v0, Bolt
│   └── Entornos reproducibles: [[GitHub Codespaces]]
│
├── 2. DESARROLLO FULL-STACK CON IA
│   ├── Frontend: React, TypeScript, Tailwind, Vitest
│   ├── Backend: [[FastAPI]], Pydantic, SQLAlchemy ORM
│   ├── Persistencia: SQLite, [[PostgreSQL]]
│   ├── Containerización: [[Docker]], Docker Compose (Multi-stage)
│   ├── Despliegue: Render Blueprint (render.yaml)
│   └── CI/CD: GitHub Actions (Testing & Quality Gate)
│
├── 3. PROTOCOLOS DE CONTEXTO
│   ├── [[Model Context Protocol (MCP)]]
│   ├── Primitivas: Tools, Resources, Prompts
│   ├── Servidores: [[Context7 MCP]], PostgreSQL, GitHub, Filesystem
│   └── Clientes: Claude Desktop, VS Code Copilot
│
├── 4. AGENTES AUTÓNOMOS DE CÓDIGO
│   ├── [[Autonomous Coding Agents]]
│   ├── OpenAI Function Calling / Tool Calling
│   ├── Herramientas del Agente: read, write, run_command
│   └── Agentic Loop (Plan -> Act -> Observe -> Correct)
│
└── 5. AUTOMATIZACIÓN LOW-CODE CON IA
    ├── [[n8n AI Workflows]]
    ├── AI Agent Node (LangChain bajo el capó)
    ├── Memoria: WindowBufferMemory
    └── Despliegue: Docker + Caddy SSL en VPS
```

---

## 🛠️ Stack Tecnológico Dominado

| Capa / Dominio | Tecnologías Principales |
|---|---|
| **Frontend & UI** | React, Vite, TypeScript, Tailwind CSS, shadcn/ui, [[Lovable]] |
| **Backend & APIs** | Python, [[FastAPI]], Pydantic, Uvicorn |
| **Bases de Datos & ORM** | SQLAlchemy, SQLite, [[PostgreSQL]] |
| **Testing & Calidad** | Vitest, React Testing Library, Pytest, TestClient |
| **DevOps & Cloud** | [[Docker]], Docker Compose, Render Platform, GitHub Actions |
| **Protocolos de IA** | [[Model Context Protocol (MCP)]], [[Context7 MCP]] |
| **Agentes & Tool Calling** | OpenAI Tools API, Agentic Loop CLI |
| **Automatización** | [[n8n AI Workflows]], Caddy Reverse Proxy |

---

## 🔗 Relaciones con Otras Series y Bóvedas
- [[Master Plan — LLM Zoomcamp]] — Fundamentos de RAG, Vector Search y Evaluación de LLMs.
- [[Master Plan — Learn Harness Engineering]] — Harness y observabilidad de sistemas agénticos.
- [[Anthropic — How to Build Effective Agents]] — Patrones de diseño agéntico de Anthropic.
- [[Context Engineering]] — Estrategias avanzadas de optimización de contexto.
"""

def main():
    print(f"Generating {len(notes)} course notes in {NOTES_DIR}...")
    for n in notes:
        target_file = NOTES_DIR / n["filename"]
        target_file.write_text(n["content"].strip() + "\n", encoding="utf-8")
        print(f"Created: {target_file.name}")

    print(f"\nGenerating {len(wiki_concepts)} wiki concepts in {WIKI_DIR}...")
    for w in wiki_concepts:
        target_file = WIKI_DIR / w["filename"]
        target_file.write_text(w["content"].strip() + "\n", encoding="utf-8")
        print(f"Created/Updated Wiki: {target_file.name}")

    print(f"\nWriting Master Plan at {MASTER_PLAN_PATH}...")
    MASTER_PLAN_PATH.write_text(master_plan_content.strip() + "\n", encoding="utf-8")
    print(f"Master Plan successfully created!")

if __name__ == "__main__":
    main()
