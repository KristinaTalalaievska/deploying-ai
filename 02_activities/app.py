import re
import logging
import requests
import gradio as gr
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
_logs = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".env")
load_dotenv("../05_src/.secrets")

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def chat_fn(message, history):
    """Handles incoming chat messages."""
    _logs.info(f"User message: {message}")

    # 1. Check for email breaches
    emails = re.findall(EMAIL_REGEX, message)
    if emails:
        try:
            response = requests.get("http://127.0.0.1:8001/breach", params={"message": message}, timeout=10)
            if response.status_code == 200:
                return response.json().get("response", "Breach check complete.")
            return "Error: breach service unavailable."
        except Exception as e:
            _logs.error(f"Breach service error: {e}")
            return "Error connecting to breach service."

    # 2. Otherwise, ask the cybersecurity semantic search
    try:
        response = requests.get("http://127.0.0.1:8002/search", params={"q": message}, timeout=10)
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                reply = "\n\n".join(
                    [f"{i+1}. {item['text']} (score: {item['score']:.2f})" for i, item in enumerate(results[:3])]
                )
                return reply
            return "No relevant cybersecurity information found."
        return "Error: semantic service unavailable."
    except Exception as e:
        _logs.error(f"Semantic service error: {e}")
        return "Error connecting to semantic search service."

# Gradio UI
with gr.Blocks(theme=gr.themes.Default()) as demo:
    gr.Markdown("# Cybersecurity Assistant")
    gr.Markdown("Ask about cyber threats, prevention, or check emails for breaches.")
    chatbot = gr.Chatbot(type="messages", height=400)
    msg = gr.Textbox(label="Your message", placeholder="Ask about cybersecurity or check an email...")
    clear = gr.Button("Clear")

    def respond(message, chat_history):
        response = chat_fn(message, chat_history)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response})
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    _logs.info("Starting Cybersecurity Assistant...")
    demo.launch(server_name="127.0.0.1", server_port=7860)