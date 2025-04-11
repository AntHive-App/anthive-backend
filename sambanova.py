import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Verify API key is set
api_key = os.getenv("SAMBANOVA_API_KEY")
if not api_key:
    raise ValueError("SAMBANOVA_API_KEY not found in environment variables")

print("API Key found, initializing client...")

client = OpenAI(
    base_url="https://api.sambanova.ai/v1",
    api_key=api_key
)

# Test the connection
print("Testing API connection...")
try:
    # Make a simple API call to verify connection
    test_response = client.models.list()
    print("API connection successful!")
except Exception as e:
    print(f"Error connecting to SambaNova API: {e}")
    raise

def generate_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="E5-Mistral-7B-Instruct",
        input=text
    )

    print(response.data[0].embedding)

def process_text(text: str):
    print("Starting process_text function...")
    system_prompt = """
    You are a JSON response generator. Given the input text, you must return a JSON object with the following structure:
    {
        "summary": "a short summary of the text",
        "language": "ISO language code",
        "flashcards": [
            {"question": "question 1", "answer": "answer 1"},
            {"question": "question 2", "answer": "answer 2"},
            {"question": "question 3", "answer": "answer 3"}
        ],
        "quiz": [
            {
                "question": "question 1",
                "options": ["option 1", "option 2", "option 3", "option 4"],
                "correct_answer": "option 1"
            },
            {
                "question": "question 2",
                "options": ["option 1", "option 2", "option 3", "option 4"],
                "correct_answer": "option 2"
            },
            {
                "question": "question 3",
                "options": ["option 1", "option 2", "option 3", "option 4"],
                "correct_answer": "option 3"
            }
        ]
    }
    
    Return ONLY the JSON object, with no additional text or explanation.
    """

    print("Making API call to SambaNova...")
    try:
        completion = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
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
        raise

# Test the function
print("Starting test...")
result = process_text("""What makes a founder stand out to you?
After 15 years of working with incredible makers and founders, I helped my co-founder, Michael (in addition to being a great cofounder and investor, Michael is a great writer) distill the characteristics we tend to look for. There are eight of them and they are (briefly) — edge control; crawl-walk-run; hyperfluency; emotional depth & resilience; sustaining motivation; the alpha-gamma tensive brilliance; egoless ambition; and Friday-night-Dyson-sphere. 

Talking about all of them would turn this email into a book (one that Michael has already written!) so I'm going to just talk about something that emerges in the most incredible founders. Their ability to make the journey in the first place. For some founders, there's this pre-ordained, closely held childhood mission that they're seeking to fulfill. For others, it's more complicated. I think there's a tendency to think that one of these groups is somehow different from the other. But I think that's taking the wrong lesson — just because someone's journey takes place in a different way at a different pace, doesn't mean that they're more (or less) than others. 

What matters - and I think this is the true lesson of the Fellowship - is the ability and courage to make the journey at all. The Fellowship was about making conscious choices about your education, and I think that the most (or, least) surprising lesson of all is that the people who thrive no matter where their path takes them are the people who can make conscious choices about their life. 

Maybe it has to do with the tension in their core that makes them insider-outsiders who can see the paths not taken. Maybe it's the inner conviction that sustains them. But there's something about the most incredible founders that makes them step up to the plate.

One of our young, high school founders recently told me that working on his startup had led him to step up to the plate with his family. He went up to his absentee father and brought him and his mother together for his brother's birthday. That kind of emotional depth, maturity is rare in a 40 year old, let alone in a teenager.

I think that kind of person would stand out anywhere, including an investor meeting. It's rare to find people who can make conscious choices about difficult things and then follow through.

How do you spot founders with “hyper-fluency” regarding their vision and steps to achieve it?
My co-founder, Michael, loves to say that it's as distinctive as the pop of a fastball hitting a catcher’s mitt. I remember when I met Austin during a summit and I went, "Ohhhh so you're really into lasers." He knew everything about lasers and LIDAR backwards, forwards, sideways and inside-out - and he couldn't stop talking about it! His knowledge went way beyond what the average smart person would learn about their market. He knew details that made it very clear that LIDAR and lasers were his obsession.

This kind of obsessive focus is pretty often mixed with an intense curiosity about the world that's so different from the way most people live their daily lives. And it does make a lot of sense. To get into something in obsessive detail, you need to have some type of intense curiosity driving you in the first place. And it doesn't stop in one place.

I have a friend who is obsessed with space and she was telling me about an astronaut who is the type of person who looks at their morning coffee (in space) and wonders if he can model the early solar system with salt, sugar and coffee. He can talk your ear off about fluid dynamics but he has also done emergency dental surgery, repaired snowmobiles, macgyvered stuff in space, invented a 0g coffee cup, published a book about his art and spent his time in space playing with physics. He's NASA's oldest astronaut and he loves his job. It's clear that he was built for his job - to be an astronaut.

That's what we're looking for. We're looking for founders with that kind of tensive brilliance and hyperfluency who're just built for the markets they want to serve.""")
print("Final result:", result)