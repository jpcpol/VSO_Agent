# SSPA VSO — Despliegue CPU (Ryzen 5 / 16 GB RAM)

## Cambios respecto a la versión original

| Componente | Original | CPU-optimizado |
|---|---|---|
| Modelo LLM | `llama3:8b` (~6 GB RAM) | `qwen2:1.5b` (~2.5 GB RAM) |
| Torch | Con CUDA (~8 GB imagen) | CPU-only (~2 GB imagen) |
| Ollama GPU | `deploy.resources` NVIDIA | Sin restricciones GPU |
| ChromaDB | Re-indexa siempre | Persiste en volumen Docker |
| Contexto RAG | 3 chunks de 800 tokens | 3 chunks de 600 tokens |
| Inicio bot | Sin espera de Ollama | `healthcheck` + `model-puller` |
| Caché | Sin caché | `lru_cache(128)` en queries |
| Imagen Docker | 1 etapa | 2 etapas (builder + runtime) |

## Requisitos del host

- Docker Desktop o Docker Engine + Compose v2
- 16 GB RAM (el stack consume ~8–10 GB en total)
- Ryzen 5 (recomendado con 6 núcleos habilitados para OMP)
- ~10 GB de espacio libre en disco (imagen + modelo)

## Guía de inicio rápido

```bash
# 1. Clonar / descomprimir el proyecto
cp .env.example .env
nano .env   # ← pega tu TELEGRAM_BOT_TOKEN

# 2. Construir e iniciar (la primera vez tarda ~10 min por descarga del modelo)
docker compose up --build

# 3. Verificar que todo está OK
docker compose ps
docker logs sspa_vso_agent -f
```

## Modelos alternativos (editar MODEL_NAME en .env)

```
qwen2:1.5b   → ~2.5 GB RAM  ✅ Por defecto — rápido, buen español
phi3:mini    → ~2.3 GB RAM  ✅ Buena alternativa
llama3.2:3b  → ~3.5 GB RAM  ⚠  Más lento pero mejor calidad
llama3:8b    → ~6 GB RAM    ❌ No recomendado en Ryzen 5 sin GPU
```

## Estimación de tiempos de respuesta (Ryzen 5 5600)

| Modelo | Primera respuesta | Respuestas siguientes |
|---|---|---|
| `qwen2:1.5b` | ~8–15 seg | ~5–10 seg |
| `phi3:mini` | ~10–18 seg | ~6–12 seg |
| `llama3.2:3b` | ~25–40 seg | ~15–25 seg |

> Las respuestas cacheadas (`lru_cache`) son instantáneas.

## Solución de problemas frecuentes

**El bot no responde / timeout**
```bash
docker logs sspa_ollama_vso --tail 50
# Si el modelo no está descargado aún, esperar a model-puller
```

**OOM (Out of Memory)**
```bash
# Reducir mem_limit en docker-compose.yml, o cambiar a qwen2:1.5b
```

**Re-indexar los manuales (después de actualizarlos)**
```bash
docker compose down
docker volume rm sspa_vector_db
docker compose up
```
