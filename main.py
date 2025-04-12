from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sambanova import generate_summary
from supabase_client import save_note

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class NoteRequest(BaseModel):
    title: str
    content: str
    user_id: str  # UUID from auth.users
    folder_id: str  # UUID from folders table
    source_type: str  # 'file', 'youtube', 'audio', 'text', 'live'
    source_url: Optional[str] = None
    language: Optional[str] = None

@app.post("/process-note")
def process_note(payload: NoteRequest):
    try:
        print("Processing note with content:", payload.content)
        summary = generate_summary(payload.content)
        
        # Validate the summary response
        if not isinstance(summary, dict):
            raise HTTPException(status_code=500, detail="Invalid summary response format")
            
        if "title" not in summary:
            raise HTTPException(status_code=500, detail="Summary missing title")

        # Generate embedding for the content
        # embedding = generate_embedding(payload.content)
        
        # Convert summary to text format
        
        
        note_data = {
            "title": summary["title"],
            "content": payload.content,
            "user_id": payload.user_id,
            "folder_id": payload.folder_id,
            "source_type": payload.source_type,
            "source_url": payload.source_url,
            "language": payload.language,
            "summary": summary["summary"],  # Now a plain text string #
            "quiz_questions": None,  # Can be updated later
        }
        
        print("Processed note data:", note_data)
        
        # Save note to Supabase
        saved_note = save_note(note_data)
        if not saved_note:
            raise HTTPException(status_code=500, detail="Failed to save note to database")
            
        return {"status": "success", "note": saved_note}

    except Exception as e:
        print(f"Error processing note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)