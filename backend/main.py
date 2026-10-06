import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend import config, db, helpers

app = FastAPI(title="EchoMind")

# The frontend runs on a different port, so the browser needs permission
# to call this server. This middleware allows it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Make sure the uploads folder exists
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"ok": True, "name": "EchoMind"}


@app.post("/voice")
async def add_voice(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
):
    # Save the uploaded file to disk
    path = os.path.join(config.UPLOAD_FOLDER, audio.filename or "clip.wav")
    with open(path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Turn speech into text
    text = helpers.speech_to_text(path)

    # Find people, places, dates in the text
    entities = helpers.find_entities(text)

    # Save it
    db.save_memory(user_id, text, entities)

    return {"text": text, "entities": entities}


@app.get("/memories/{user_id}")
def get_memories(user_id: str, limit: int = 25):
    return db.list_memories(user_id, limit)


@app.get("/suggest/{user_id}")
def suggest(user_id: str):
    """Pick a memory that mentions a person and suggest talking about them."""
    mems = db.list_memories(user_id, 15)

    if not mems:
        return {"suggestion": "Start by telling me about your day."}

    for m in mems:
        people = [e for e in m["entities"] if e["kind"] == "person"]
        if people:
            name = people[0]["name"]
            return {"suggestion": f"You mentioned {name}. Want to share more about them?"}

    return {"suggestion": f'Last time you said: "{mems[0]["text"][:80]}..."'}