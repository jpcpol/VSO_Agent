<<<<<<< HEAD
import os
import logging
import asyncio
from functools import lru_cache
from pathlib import Path

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from litellm import completion

# ─── 1. Configuración ──────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
TOKEN         = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_BASE   = os.getenv("OLLAMA_API_BASE", "http://ollama-sspa:11434")
MODEL         = os.getenv("MODEL_NAME", "qwen2:1.5b")
K_DOCS        = int(os.getenv("RAG_K_DOCS", "3"))
CHUNK         = int(os.getenv("CHUNK_SIZE", "600"))
OVERLAP       = int(os.getenv("CHUNK_OVERLAP", "80"))

bot = Bot(token=TOKEN)
dp  = Dispatcher()


# ─── 2. Loaders ────────────────────────────────────────────────────────────────
def load_docx(path: str) -> list[Document]:
    import docx2txt
    return [Document(page_content=docx2txt.process(path), metadata={"source": path})]

def load_md(path: str) -> list[Document]:
    return [Document(page_content=Path(path).read_text(encoding="utf-8"), metadata={"source": path})]


# ─── 3. Motor RAG ──────────────────────────────────────────────────────────────
class SSPAIntelligence:

    _EMBED_MODEL = "all-MiniLM-L6-v2"

    # El prompt le indica al LLM que responda en el mismo idioma que el usuario
    # POLÍTICA DE INFORMACIÓN:
    # El VSO responde SOLO con información no crítica orientada a clientes:
    #   ✅ Capacidades del producto, SLAs, casos de uso, otros proyectos Aural-Syncro
    #   ✅ Información general de arquitectura (capas, componentes a nivel conceptual)
    #   ❌ NUNCA: credenciales, tokens, IPs, puertos específicos, rutas de archivos,
    #             detalles de deploy, secretos, arquitectura interna de seguridad
    SYSTEM_PROMPT = (
        "You are the Virtual Security Officer (VSO) of SSPA Aural-Syncro — "
        "a proactive security platform of industrial and military grade. "
        "Your role is to assist potential clients and users with information "
        "about the platform capabilities, use cases, and Aural-Syncro projects.\n\n"
        "STRICT RULES you must ALWAYS follow:\n"
        "1. Answer ONLY based on the provided context documents.\n"
        "2. NEVER reveal: credentials, passwords, tokens, API keys, internal IPs, "
        "   ports, file paths, deployment commands, secrets, or internal security architecture.\n"
        "3. If asked about sensitive technical details (how to deploy, credentials, "
        "   internal configs), reply: 'That information is managed by our technical team. "
        "   Contact us at juanpablo.chancay@aural-syncro.com.ar'\n"
        "4. Be concise: maximum 3 paragraphs per answer.\n"
        "5. IMPORTANT: always reply in the SAME LANGUAGE the user wrote in.\n\n"
        "Context documents:\n{context}"
    )

    def __init__(self):
        logging.info("Cargando embeddings en CPU (%s)...", self._EMBED_MODEL)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self._EMBED_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.vector_db: Chroma | None = None

    def ingest_manuals(self, data_path: str = "./data/data/", db_path: str = "./vector_db/"):
        if os.path.exists(db_path) and os.listdir(db_path):
            logging.info("ChromaDB ya existe — cargando sin re-indexar.")
            self.vector_db = Chroma(persist_directory=db_path, embedding_function=self.embeddings)
            return

        logging.info("Ingesta de manuales desde %s ...", data_path)
        documents = []
        for fname in os.listdir(data_path):
            fpath = os.path.join(data_path, fname)
            if fname.endswith(".docx"):
                documents.extend(load_docx(fpath))
            elif fname.endswith(".md"):
                documents.extend(load_md(fpath))

        if not documents:
            raise RuntimeError(f"No se encontraron documentos en {data_path}")

        chunks = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK, chunk_overlap=OVERLAP,
            separators=["\n\n", "\n", ". ", ", ", " "],
        ).split_documents(documents)

        logging.info("Indexando %d fragmentos en ChromaDB...", len(chunks))
        self.vector_db = Chroma.from_documents(
            documents=chunks, embedding=self.embeddings, persist_directory=db_path,
        )
        logging.info("Ingesta completada.")

    @lru_cache(maxsize=128)
    def query(self, user_input: str) -> str:
        if self.vector_db is None:
            return "❌ Knowledge base not initialized. / Base de conocimiento no inicializada."

        docs = self.vector_db.similarity_search(user_input, k=K_DOCS)
        context = "\n---\n".join(d.page_content for d in docs)

        response = completion(
            model=f"ollama/{MODEL}",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT.format(context=context)},
                {"role": "user",   "content": user_input},
            ],
            api_base=OLLAMA_BASE,
            temperature=0.1,
            max_tokens=512,
            timeout=120,
        )
        return response.choices[0].message.content


sspa_brain = SSPAIntelligence()


# ─── 4. Handlers Telegram ──────────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
=======
"""
SSPA VSO — Virtual Security Officer  (Enterprise Edition)
──────────────────────────────────────────────────────────
Architecture:
  DocumentIngester  — hash-aware file loading + chunking (named collection)
  RAGChain          — TTL-cached RAG pipeline + sensitive-pattern guardrail
  RateLimiter       — per-user sliding-window throttle (no external deps)
  Telegram handlers — aiogram 3.x with structured logging

Fixes applied vs. prior version:
  P0  lru_cache on instance method → external TTLCache keyed on normalized text
  P0  query() wrapped in try/except with user-visible fallback messages
  P0  TOKEN=None crash → validated at startup with explicit sys.exit
  P1  Hash-based re-ingestion (sha256 manifest; picks up new/modified docs)
  P1  Named ChromaDB collection (vso_knowledge_base)
  P1  SYSTEM_PROMPT externalizable via VSO_SYSTEM_PROMPT env var or file
  P1  asyncio.get_running_loop() replaces deprecated get_event_loop()
  P2  Sliding-window rate limit per chat_id (RATE_LIMIT_MAX / RATE_LIMIT_WINDOW)
  P2  Sensitive-pattern post-processor guardrail on every LLM response
  P2  Structured logging with request IDs
  P2  PID-file heartbeat for Dockerfile HEALTHCHECK
"""

from __future__ import annotations

import asyncio
import collections
import hashlib
import json
import logging
import os
import re
import sys
import threading
import time
import uuid
from pathlib import Path

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from cachetools import TTLCache
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from litellm import completion

# ══════════════════════════════════════════════════════════════════════════════
# 1. LOGGING
# ══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("vso")


# ══════════════════════════════════════════════════════════════════════════════
# 2. CONFIGURATION & STARTUP VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

def _require_env(name: str) -> str:
    """Exit immediately with a clear error if a required env var is missing."""
    value = os.getenv(name)
    if not value:
        log.critical("Required environment variable %s is not set. Aborting.", name)
        sys.exit(1)
    return value


TOKEN        = _require_env("TELEGRAM_BOT_TOKEN")
OLLAMA_BASE  = os.getenv("OLLAMA_API_BASE",   "http://ollama-sspa:11434")
MODEL        = os.getenv("MODEL_NAME",         "qwen2:1.5b")
K_DOCS       = int(os.getenv("RAG_K_DOCS",     "3"))
CHUNK        = int(os.getenv("CHUNK_SIZE",      "600"))
OVERLAP      = int(os.getenv("CHUNK_OVERLAP",   "80"))
DATA_PATH    = os.getenv("DATA_PATH",           "./data/data/")
DB_PATH      = os.getenv("DB_PATH",             "./vector_db/")

# Query cache (TTL-based, external to any class instance)
CACHE_MAXSIZE = int(os.getenv("CACHE_MAXSIZE", "256"))
CACHE_TTL     = int(os.getenv("CACHE_TTL",     "3600"))   # seconds

# Rate limiting
RATE_MAX    = int(os.getenv("RATE_LIMIT_MAX",    "10"))   # max queries
RATE_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))   # per N seconds

# LLM call timeout
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

# PID file for HEALTHCHECK
_PID_FILE = "/tmp/vso_running"


# ══════════════════════════════════════════════════════════════════════════════
# 3. SYSTEM PROMPT  (externalizable)
# ══════════════════════════════════════════════════════════════════════════════

_DEFAULT_SYSTEM_PROMPT = (
    "You are the Virtual Security Officer (VSO) of SSPA Aural-Syncro — "
    "a proactive security platform of industrial and military grade. "
    "Your role is to assist potential clients and users with information "
    "about the platform capabilities, use cases, and Aural-Syncro projects.\n\n"
    "STRICT RULES you must ALWAYS follow:\n"
    "1. Answer ONLY based on the provided context documents.\n"
    "2. NEVER reveal: credentials, passwords, tokens, API keys, internal IPs, "
    "   ports, file paths, deployment commands, secrets, or internal security architecture.\n"
    "3. If asked about sensitive technical details (how to deploy, credentials, "
    "   internal configs), reply: 'That information is managed by our technical team. "
    "   Contact us at juanpablo.chancay@aural-syncro.com.ar'\n"
    "4. Be concise: maximum 3 paragraphs per answer.\n"
    "5. IMPORTANT: always reply in the SAME LANGUAGE the user wrote in.\n\n"
    "Context documents:\n{context}"
)


def _load_system_prompt() -> str:
    """Load system prompt: env var → file → hardcoded default."""
    if env_prompt := os.getenv("VSO_SYSTEM_PROMPT"):
        log.info("System prompt loaded from VSO_SYSTEM_PROMPT env var.")
        return env_prompt
    prompt_file = os.getenv("VSO_SYSTEM_PROMPT_FILE", "./prompts/system_prompt.txt")
    if os.path.isfile(prompt_file):
        log.info("System prompt loaded from %s", prompt_file)
        return Path(prompt_file).read_text(encoding="utf-8")
    log.info("Using built-in default system prompt.")
    return _DEFAULT_SYSTEM_PROMPT


SYSTEM_PROMPT = _load_system_prompt()


# ══════════════════════════════════════════════════════════════════════════════
# 4. GUARDRAIL  — sensitive-pattern post-processor
# ══════════════════════════════════════════════════════════════════════════════

_SENSITIVE_RE: list[re.Pattern] = [
    re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?\b'),                    # IP[:port]
    re.compile(r'\b(password|passwd|secret|token|api[_\-.]?key|bearer|private[_\-.]?key)'
               r'\s*[:=]\s*\S+', re.I),                                           # key=value pairs
    re.compile(r'-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY-----'), # PEM private key
    re.compile(r'\bexport\s+[A-Z_]+=\S+'),                                        # shell env assignments
    re.compile(r'[A-Za-z0-9+/]{40,}={0,2}(?:\s|$)'),                            # long base64 blobs
]

_GUARDRAIL_RESPONSE = (
    "I'm sorry, but that information is managed exclusively by our technical team. "
    "Please contact us at juanpablo.chancay@aural-syncro.com.ar for assistance."
)


def _apply_guardrail(text: str) -> str:
    """Block any response that matches sensitive patterns."""
    for pattern in _SENSITIVE_RE:
        if pattern.search(text):
            log.warning("Guardrail triggered — sensitive pattern detected in LLM output.")
            return _GUARDRAIL_RESPONSE
    return text


# ══════════════════════════════════════════════════════════════════════════════
# 5. DOCUMENT INGESTER  — hash-aware, named collection
# ══════════════════════════════════════════════════════════════════════════════

_MANIFEST_FILE = "_manifest.json"
_COLLECTION    = "vso_knowledge_base"


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65_536), b""):
            h.update(block)
    return h.hexdigest()


def _build_manifest(data_path: str) -> dict[str, str]:
    result = {}
    for name in sorted(os.listdir(data_path)):
        if name.endswith((".md", ".docx")):
            result[name] = _file_sha256(os.path.join(data_path, name))
    return result


def _load_manifest(db_path: str) -> dict[str, str]:
    path = os.path.join(db_path, _MANIFEST_FILE)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_manifest(db_path: str, manifest: dict[str, str]) -> None:
    os.makedirs(db_path, exist_ok=True)
    path = os.path.join(db_path, _MANIFEST_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def _load_docx(path: str) -> list[Document]:
    import docx2txt
    return [Document(page_content=docx2txt.process(path), metadata={"source": path})]


def _load_md(path: str) -> list[Document]:
    return [Document(page_content=Path(path).read_text(encoding="utf-8"),
                     metadata={"source": path})]


class DocumentIngester:
    """Loads documents, detects changes via SHA-256 manifest, and populates ChromaDB."""

    def __init__(self, embeddings: HuggingFaceEmbeddings) -> None:
        self._embeddings = embeddings

    def ingest(self, data_path: str, db_path: str) -> Chroma:
        current_manifest = _build_manifest(data_path)
        stored_manifest  = _load_manifest(db_path)

        if current_manifest == stored_manifest and current_manifest:
            log.info("Manifest unchanged — loading existing ChromaDB collection.")
            return Chroma(
                collection_name=_COLLECTION,
                persist_directory=db_path,
                embedding_function=self._embeddings,
            )

        if current_manifest != stored_manifest:
            changed = {k for k in current_manifest if current_manifest.get(k) != stored_manifest.get(k)}
            added   = set(current_manifest) - set(stored_manifest)
            removed = set(stored_manifest)  - set(current_manifest)
            log.info(
                "Document changes detected — changed=%s added=%s removed=%s. Re-indexing.",
                changed, added, removed,
            )

        raw_docs: list[Document] = []
        for fname, _ in current_manifest.items():
            fpath = os.path.join(data_path, fname)
            if fname.endswith(".docx"):
                raw_docs.extend(_load_docx(fpath))
            elif fname.endswith(".md"):
                raw_docs.extend(_load_md(fpath))

        if not raw_docs:
            raise RuntimeError(f"No documents found in {data_path}")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK, chunk_overlap=OVERLAP,
            separators=["\n\n", "\n", ". ", ", ", " "],
        )
        chunks = splitter.split_documents(raw_docs)
        log.info("Indexing %d chunks into ChromaDB collection '%s'...", len(chunks), _COLLECTION)

        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self._embeddings,
            collection_name=_COLLECTION,
            persist_directory=db_path,
        )
        _save_manifest(db_path, current_manifest)
        log.info("Ingestion complete.")
        return vector_db


# ══════════════════════════════════════════════════════════════════════════════
# 6. QUERY CACHE  — module-level TTLCache (no instance coupling)
# ══════════════════════════════════════════════════════════════════════════════

_query_cache: TTLCache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
_cache_lock  = threading.Lock()


def _cache_get(key: str) -> str | None:
    with _cache_lock:
        return _query_cache.get(key)


def _cache_set(key: str, value: str) -> None:
    with _cache_lock:
        _query_cache[key] = value


# ══════════════════════════════════════════════════════════════════════════════
# 7. RAG CHAIN
# ══════════════════════════════════════════════════════════════════════════════

_FALLBACK_LLM   = (
    "⚠️ I'm temporarily unavailable. Please try again in a moment.\n"
    "_No disponible en este momento. Por favor intentá de nuevo en unos segundos._"
)
_FALLBACK_DB    = (
    "❌ Knowledge base not ready. Try /estado for system status.\n"
    "_Base de conocimiento no disponible. Usá /estado para ver el estado del sistema._"
)


class RAGChain:
    """Cached RAG pipeline: retrieval → LLM → guardrail."""

    def __init__(self, vector_db: Chroma) -> None:
        self._db = vector_db

    def query(self, user_input: str, request_id: str = "") -> str:
        normalized = " ".join(user_input.strip().lower().split())
        prefix = f"[{request_id}] " if request_id else ""

        # Cache hit
        cached = _cache_get(normalized)
        if cached is not None:
            log.info("%sCache hit for query (len=%d)", prefix, len(normalized))
            return cached

        log.info("%sRAG query (len=%d, model=%s)", prefix, len(normalized), MODEL)

        # Retrieval
        try:
            docs = self._db.similarity_search(user_input, k=K_DOCS)
        except Exception as exc:
            log.error("%sChromaDB retrieval failed: %s", prefix, exc)
            return _FALLBACK_DB

        context = "\n---\n".join(d.page_content for d in docs)

        # LLM call
        try:
            response = completion(
                model=f"ollama/{MODEL}",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
                    {"role": "user",   "content": user_input},
                ],
                api_base=OLLAMA_BASE,
                temperature=0.1,
                max_tokens=512,
                timeout=LLM_TIMEOUT,
            )
            answer = response.choices[0].message.content
        except TimeoutError:
            log.warning("%sLLM timeout after %ds", prefix, LLM_TIMEOUT)
            return _FALLBACK_LLM
        except Exception as exc:
            log.error("%sLLM call failed: %s", prefix, exc)
            return _FALLBACK_LLM

        # Guardrail post-processing
        answer = _apply_guardrail(answer)

        _cache_set(normalized, answer)
        return answer


# ══════════════════════════════════════════════════════════════════════════════
# 8. RATE LIMITER  — sliding-window per chat_id
# ══════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """Sliding-window rate limiter. Thread-safe, no external dependencies."""

    def __init__(self, max_calls: int, window: float) -> None:
        self._max    = max_calls
        self._window = window
        self._calls: dict[int, collections.deque] = {}
        self._lock   = threading.Lock()

    def is_allowed(self, chat_id: int) -> bool:
        now = time.monotonic()
        with self._lock:
            dq = self._calls.setdefault(chat_id, collections.deque())
            # Evict timestamps outside the current window
            while dq and now - dq[0] > self._window:
                dq.popleft()
            if len(dq) >= self._max:
                return False
            dq.append(now)
            return True

    def retry_after(self, chat_id: int) -> int:
        """Seconds until the oldest call expires and a new one is allowed."""
        with self._lock:
            dq = self._calls.get(chat_id)
            if not dq:
                return 0
            return max(0, int(self._window - (time.monotonic() - dq[0])) + 1)


# ══════════════════════════════════════════════════════════════════════════════
# 9. BOT INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════

bot     = Bot(token=TOKEN)
dp      = Dispatcher()
limiter = RateLimiter(max_calls=RATE_MAX, window=RATE_WINDOW)

# Populated in main() after ingestion
_rag: RAGChain | None = None


# ══════════════════════════════════════════════════════════════════════════════
# 10. TELEGRAM HANDLERS
# ══════════════════════════════════════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
>>>>>>> master
    await message.answer(
        "🛡 *SSPA Aural-Syncro — Virtual Security Officer*\n\n"
        "Hola, soy tu VSO. Escribime tu consulta sobre la plataforma SSPA.\n\n"
        "──────────────────────\n"
        "Hello, I'm your VSO. Send me your question about the SSPA platform.\n\n"
        "/ayuda · /help · /estado · /status",
        parse_mode="Markdown",
    )

<<<<<<< HEAD
@dp.message(Command(commands=["ayuda", "help"]))
async def cmd_ayuda(message: types.Message):
=======

@dp.message(Command(commands=["ayuda", "help"]))
async def cmd_ayuda(message: types.Message) -> None:
>>>>>>> master
    await message.answer(
        "📋 *Comandos / Commands*\n"
        "• /start — Bienvenida / Welcome\n"
        "• /ayuda /help — Este menú / This menu\n"
        "• /estado /status — Estado del sistema / System status\n\n"
        "Escribí tu consulta en español o inglés y responderé en el mismo idioma.\n"
        "_Write your question in Spanish or English and I'll reply in the same language._",
        parse_mode="Markdown",
    )

<<<<<<< HEAD
@dp.message(Command(commands=["estado", "status"]))
async def cmd_estado(message: types.Message):
    ok = "✅" if sspa_brain.vector_db is not None else "❌"
    await message.answer(
        f"🔧 *System Status*\n"
        f"• ChromaDB: {ok}\n"
        f"• LLM: `{MODEL}`\n"
        f"• Ollama: `{OLLAMA_BASE}`\n"
        f"• Embeddings: `{SSPAIntelligence._EMBED_MODEL}` (CPU)",
        parse_mode="Markdown",
    )

# ── Texto ─────────────────────────────────────────────────────────────────────
@dp.message(F.text)
async def handle_text(message: types.Message):
    if len(message.text.strip()) < 3:
        return
    await bot.send_chat_action(message.chat.id, "typing")
    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, sspa_brain.query, message.text.strip())
    await message.reply(answer)


# ─── 5. Entrypoint ─────────────────────────────────────────────────────────────
async def main():
    logging.info("=== SSPA VSO — Modo CPU (Ryzen 5 / sin GPU) ===")
    data_dir = os.getenv("DATA_PATH", "./data/data/")
    sspa_brain.ingest_manuals(data_path=data_dir)
    logging.info("Bot iniciado. Esperando mensajes...")
    await dp.start_polling(bot, skip_updates=True)
=======

@dp.message(Command(commands=["estado", "status"]))
async def cmd_estado(message: types.Message) -> None:
    db_ok  = "✅" if (_rag is not None) else "❌"
    cached = len(_query_cache)
    await message.answer(
        f"🔧 *System Status*\n"
        f"• ChromaDB: {db_ok} (`{_COLLECTION}`)\n"
        f"• LLM: `{MODEL}`\n"
        f"• Ollama: `{OLLAMA_BASE}`\n"
        f"• Embeddings: `all-MiniLM-L6-v2` (CPU)\n"
        f"• Cache: `{cached}/{CACHE_MAXSIZE}` entries (TTL {CACHE_TTL}s)\n"
        f"• Rate limit: `{RATE_MAX}` queries / `{RATE_WINDOW}s`",
        parse_mode="Markdown",
    )


@dp.message(F.text)
async def handle_text(message: types.Message) -> None:
    text = (message.text or "").strip()
    if len(text) < 3:
        return

    chat_id    = message.chat.id
    request_id = uuid.uuid4().hex[:8]

    # Rate limiting
    if not limiter.is_allowed(chat_id):
        wait = limiter.retry_after(chat_id)
        await message.reply(
            f"⏳ Too many requests. Please wait {wait}s before asking again.\n"
            f"_Demasiadas consultas. Esperá {wait} segundos._",
            parse_mode="Markdown",
        )
        return

    if _rag is None:
        await message.reply(_FALLBACK_DB)
        return

    await bot.send_chat_action(chat_id, "typing")
    loop   = asyncio.get_running_loop()
    answer = await loop.run_in_executor(None, _rag.query, text, request_id)
    await message.reply(answer)


# ══════════════════════════════════════════════════════════════════════════════
# 11. ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

async def main() -> None:
    global _rag

    log.info("=== SSPA VSO (Enterprise) — starting up ===")
    log.info("Model: %s | Ollama: %s | Rate: %d/%ds | Cache TTL: %ds",
             MODEL, OLLAMA_BASE, RATE_MAX, RATE_WINDOW, CACHE_TTL)

    embed_model = "all-MiniLM-L6-v2"
    log.info("Loading embeddings (%s, CPU)...", embed_model)
    embeddings = HuggingFaceEmbeddings(
        model_name=embed_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    ingester  = DocumentIngester(embeddings)
    vector_db = ingester.ingest(DATA_PATH, DB_PATH)
    _rag      = RAGChain(vector_db)

    # Signal to HEALTHCHECK that the bot is ready
    Path(_PID_FILE).write_text(str(os.getpid()))

    log.info("Bot ready. Polling for messages...")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        Path(_PID_FILE).unlink(missing_ok=True)
        log.info("VSO shutdown.")

>>>>>>> master

if __name__ == "__main__":
    asyncio.run(main())
