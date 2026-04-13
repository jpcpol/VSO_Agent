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
    await message.answer(
        "🛡 *SSPA Aural-Syncro — Virtual Security Officer*\n\n"
        "Hola, soy tu VSO. Escribime tu consulta sobre la plataforma SSPA.\n\n"
        "──────────────────────\n"
        "Hello, I'm your VSO. Send me your question about the SSPA platform.\n\n"
        "/ayuda · /help · /estado · /status",
        parse_mode="Markdown",
    )

@dp.message(Command(commands=["ayuda", "help"]))
async def cmd_ayuda(message: types.Message):
    await message.answer(
        "📋 *Comandos / Commands*\n"
        "• /start — Bienvenida / Welcome\n"
        "• /ayuda /help — Este menú / This menu\n"
        "• /estado /status — Estado del sistema / System status\n\n"
        "Escribí tu consulta en español o inglés y responderé en el mismo idioma.\n"
        "_Write your question in Spanish or English and I'll reply in the same language._",
        parse_mode="Markdown",
    )

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

if __name__ == "__main__":
    asyncio.run(main())
