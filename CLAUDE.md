# VSO_Agent — Virtual Security Officer · Aural Syncro

## Descripción

Bot de Telegram con RAG (Retrieval-Augmented Generation) que actúa como asistente AI del ecosistema SSPA y Aural-Syncro. Responde consultas sobre el portfolio de productos, manuales técnicos y capacidades de la plataforma usando Ollama como LLM local y ChromaDB como vector store.

## Arquitectura

```text
Telegram API
    ↓ aiogram 3.x
app/main.py  ←── litellm → Ollama (llama3.2:3b por defecto)
    ↓
LangChain RAG
    ↓
ChromaDB (vso_vector_db) ← all-MiniLM-L6-v2 (embeddings, CPU)
    ↑
data/data/   ← knowledge base (Markdown + DOCX)
```

## Knowledge base (`data/data/`)

| Archivo | Contenido |
| ------- | --------- |
| `SSPA_Manual_Nodo.md` | Manual operativo nodo edge SSPA (Jetson, Watchdog, modelos) |
| `SSPA_Manual_SOC.md` | Manual SOC (Zabbix, WireGuard, PostgreSQL, MQTT, Redis) |
| `Aural_Syncro_Company_Pitch.md` | Posicionamiento comercial, planes, sectores, SLAs |
| `Informacion_para_Clientes_Aural_Syncro.docx` | Info de productos para clientes |
| `Otros_Proyectos_de_Aural_Syncro.docx` | Referencias a Endo-Edge LAB+, Asistente Multiagente |

## Stack

- **Bot**: aiogram >=3.13 (async Telegram)
- **LLM**: litellm → Ollama local (llama3.2:3b por defecto; alternativas: qwen2:1.5b, phi3:mini, tinyllama)
- **RAG**: LangChain 0.2 · ChromaDB 0.5 · sentence-transformers (all-MiniLM-L6-v2, CPU)
- **Doc processing**: docx2txt (DOCX) + Markdown nativo
- **Caché**: TTLCache 256 entradas · 3600s TTL
- **Rate limiting**: sliding-window por chat_id (10 req/60s por defecto)
- **Guardrails**: regex para bloquear IPs, credenciales, PEM keys, base64

## Configuración del RAG

| Variable | Default | Descripción |
| -------- | ------- | ----------- |
| `VSO_MODEL_NAME` | llama3.2:3b | Modelo Ollama a usar |
| `CHUNK_SIZE` | 600 | Tamaño de chunk en caracteres |
| `CHUNK_OVERLAP` | 80 | Solapamiento entre chunks |
| `RAG_K_DOCS` | 4 | Documentos recuperados por query |
| `CACHE_TTL` | 3600 | TTL de caché de respuestas (s) |

## Servicios Docker

| Servicio | Función |
| -------- | ------- |
| `ollama-vso` | Servidor Ollama (5 GB mem limit) |
| `vso-model-puller` | Init: descarga el modelo una sola vez |
| `vso-bot` | Bot principal (4 GB mem limit) |

## Guardrail crítico

El bot **nunca revela** IPs internas, credenciales, claves PEM ni secretos. Redirige a `juanpablo.chancay@aural-syncro.com.ar` para información sensible.

## Actualizar la knowledge base

Para que el bot aprenda información nueva:

1. Añadir o modificar archivos en `data/data/`
2. Reiniciar `vso-bot` — la ingesta es hash-aware (solo re-indexa lo que cambió)

## Wiki de Conocimiento

Wiki personal en: `c:\Users\Usuario\Documents\Aural Syncro\Obsidian`

**Consultar el wiki cuando:**

- Evalúes modelos Ollama alternativos (ver [[ollama]] y benchmarks en [[tops-metrica]])
- Compares estrategias RAG o vector stores
- Actualices la knowledge base con información de otros proyectos del ecosistema

**Actualizar el wiki cuando:**

- Documentes benchmarks de Ollama en CPU para distintos modelos
- Implementes Whisper para voice queries (infraestructura ya preparada en `.env`)
- Página a actualizar: `wiki/proyectos/vso-agent.md`
