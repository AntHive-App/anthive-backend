from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sambanova import process_text
from supabase_client import save_note

app = FastAPI()

class NoteRequest(BaseModel):
    title: str
    content: str
    user_id: str
    folder_id: str
    source_type: str  # 'file', 'youtube', etc.
    source_url: Optional[str] = None
    language: Optional[str] = None

@app.post("/process-note")
async def process_note(payload: NoteRequest):
    try:
        embedding = await generate_embedding(payload.content)
        result = await process_text(payload.content)

        note_data = {
            "title": payload.title,
            "content": payload.content,
            "user_id": payload.user_id,
            "folder_id": payload.folder_id,
            "source_type": payload.source_type,
            "source_url": payload.source_url,
            "language": payload.language,
            "embedding": result.get("embedding"),
            "summary": result.get("summary"),
            "quiz_questions": result.get("quiz"),
        }

        # saved_note = save_note(note_data)
        # return {"status": "success", "note": saved_note}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
