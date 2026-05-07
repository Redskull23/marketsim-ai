from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_connection():
    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            input="Say: OpenAI connection successful."
        )

        print("\n=== OpenAI Response ===")
        print(response.output_text)

    except Exception as e:
        print("\n=== Connection Failed ===")
        print(str(e))


if __name__ == "__main__":
    test_connection()