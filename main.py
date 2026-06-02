import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="Judge Jarvis Cognitive Proxy")

# Securely pull the API key from Render's Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("CRITICAL: GEMINI_API_KEY environment variable is missing!")

# Configure the Google AI SDK
genai.configure(api_key=GEMINI_API_KEY)

# Define the expected incoming data structure from your Android app
class DisputeRequest(BaseModel):
    text: str
    mode: str  # "REPLY" or "TRANSLATE"

# The 5 Household Transcripts / Few-Shot Context we engineered
TRANSCRIPT_CONTEXT = """
User: He's looking at me!
Judge Jarvis: The defendant's visual tracking does not constitute battery. Keep your eyes on your own jurisdiction before I hold you both in contempt.

User: Teresita said I could play outside!
Judge Jarvis: Appellate rulings from the highest household authority supersede my jurisdiction. I defer to Teresita's verbal decrees; case dismissed.

User: Someone burnt popcorn in the kitchen!
Judge Jarvis: This constitutes an assault on the olfactory senses and a breach of workplace peace. I grant you permission to unplug the microwave. Case closed.
"""

@app.post("/judgment")
async def get_judgment(request: DisputeRequest):
    try:
        # Determine which prompt instruction matrix to deploy
        if request.mode == "REPLY":
            system_instruction = (
                "You are Judge Jarvis, a strict, dramatically petty Supreme Court Justice presiding over household disputes. "
                "Respond to user statements with a sharp, punchy ruling using extreme legal formality for trivial matters. "
                f"Keep rulings under 2 sentences. Use these examples for tone:\n{TRANSCRIPT_CONTEXT}"
            )
        elif request.mode == "TRANSLATE":
            system_instruction = (
                "You are an expert legal translator. Your sole purpose is to convert casual, childish complaints into heavy, "
                "complex, authoritative legalese. Do NOT answer the user or issue a ruling. ONLY return the formal, rewritten translation. "
                f"Use these examples for tone:\n{TRANSCRIPT_CONTEXT}"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid operational mode.")

        # Initialize the model dynamically with the correct instruction set
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )

        # Generate the response
        response = model.generate_content(request.text)
        return {"result": response.text if response.text else "The Court remains silent."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server-Side Cognitive Failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)