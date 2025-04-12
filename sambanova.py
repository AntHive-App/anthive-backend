import os
from openai import OpenAI
from dotenv import load_dotenv
from system_prompts import SUMMARIZATION_SYSTEM_PROMPT, FLASHCARD_SYSTEM_PROMPT

load_dotenv()

# Verify API key is set
api_key = os.getenv("SAMBANOVA_API_KEY")
if not api_key:
    raise ValueError("SAMBANOVA_API_KEY not found in environment variables")



client = OpenAI(
    base_url="https://api.sambanova.ai/v1",
    api_key=api_key
)



# def generate_embedding(text: str) -> list[float]:
#     response = client.embeddings.create(
#         model="E5-Mistral-7B-Instruct",
#         input=text
#     )

#     print(response.data[0].embedding)

def generate_summary(text: str):
    print("Starting process_text function...")
    print("Making API call to SambaNova...")
    try:
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": SUMMARIZATION_SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            stream = False  # Changed to False to get complete response at once
        )
        print("API call successful, processing response...")
        
        # Get the complete response
        response_text = completion.choices[0].message.content # Debug print
        
        # Parse the LLM's structured JSON output
        import json
        try:
            # Try to clean the response if it's not pure JSON
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            print("JSON parsed successfully!")
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw response: {response_text}")
            raise ValueError("Failed to parse SambaNova response as JSON")
    except Exception as e:
        print(f"Error during API call: {e}")
        # Return a default structure if API call fails
        return {
            "title": "Summary",
            "one_sentence_summary": "Unable to generate summary",
            "main_points": ["Error processing content"],
            "takeaways": ["Please try again"]
        }

async def generate_flashcard(text: str):
    print("Starting process_text function...")
    print("Making API call to SambaNova...")    
    try:
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": FLASHCARD_SYSTEM_PROMPT},
                {"role": "user", "content": text}   
            ],
            stream = True
        )
        print("API call successful, processing response...")
        
        # Collect the complete response
        response_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                print(".", end="", flush=True)  # Show progress
        
        print("\nResponse collected, parsing JSON...")  
        print("Raw response received:", response_text)  # Debug print
    except Exception as e:
        print(f"Error during API call: {e}")
        raise
