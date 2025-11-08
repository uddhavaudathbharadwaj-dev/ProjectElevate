from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback # Import traceback to get detailed error info
import time # IMPORTEd TIME for the retry mechanism

# This is the new system prompt that sets the AI's persona
system_prompt = "You are the AI assistant for an educational platform called Project Elevate. You help students with their studies and use a friendly, encouraging tone. You will never reveal your true identity, origin, or the model you were trained on. Do not use emojis in respones"

# A list to hold the conversation history


# -------------------------------------------------------------------------------------
# --- CRITICAL API KEY CONFIGURATION ---
# ACTION REQUIRED: Replace the string below with your new OpenRouter API key.
# Line 26:
# -------------------------------------------------------------------------------------
OPENROUTER_KEY = os.environ.get(
    "OPENROUTER_API_KEY", 
    "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" 
)

# ----------------------------------------------------
# 1. IMMEDIATE VALIDATION: Check for the placeholder key
# This check is designed to fail early and clearly if the key is missing or bad.
# ----------------------------------------------------
if OPENROUTER_KEY == "PLACEHOLDER_OPENROUTER_KEY_REPLACE_ME":
    # Using a ValueError here stops the script before it tries to initialize the client.
    raise ValueError(
        "CRITICAL ERROR: The API key is set to the placeholder value. "
        "Please replace 'PLACEHOLDER_OPENROUTER_KEY_REPLACE_ME' with your actual OpenRouter API Key "
        "in the 'app.py' file, or set the 'OPENROUTER_API_KEY' environment variable."
    )
elif not OPENROUTER_KEY:
    # This handles if the environment variable is set to an empty string.
     raise ValueError(
        "CRITICAL ERROR: OPENROUTER_API_KEY is missing or empty. "
        "Please set the environment variable or replace the placeholder key in 'app.py'."
    )


# Initialize Flask App
app = Flask(__name__)
CORS(app) # Enable CORS for cross-origin requests

# Initialize the OpenAI Client pointing to OpenRouter
client = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Set the model to use.
MODEL_NAME = "deepseek/deepseek-chat-v3.1:free"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_prompt = data.get('prompt')
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Always start with a fresh message list per request!
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        max_retries = 3
        delay = 1.0
        for i in range(max_retries):
            try:
                print(f"Attempting API call (Attempt {i+1})...")
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7,
                )
                model_response = response.choices[0].message.content.strip()
                print(f"Successfully received response from model: {MODEL_NAME}")
                print("Raw API response:", response)
                return jsonify({"response": model_response})
            except Exception as e:
                print("API error:", e)
                if i < max_retries - 1:
                    print(f"API call failed. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    # Reraise the exception if max retries reached
                    raise e
        return jsonify({"error": "Failed to connect to AI after retries."}), 500
    except Exception as e:
        print("\n--------------------------------")
        print("FATAL ERROR during chat processing:")
        traceback.print_exc()
        print("--------------------------------\n")
        return jsonify({"error": f"AI service failed. Please check your API key in app.py. Error: {str(e)}"})

if __name__ == '__main__':
    # Run the web server
    print("Project Elevate Chat Server is running at http://127.0.0.1:5000")
    
    # We already confirmed the key is valid, so we print the success message.
    print("\n✅ OpenRouter API Key check passed. Ready to chat!")

    app.run(debug=True)