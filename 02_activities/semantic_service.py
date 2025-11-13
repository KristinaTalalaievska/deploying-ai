from flask import Flask, request, jsonify

app = Flask(__name__)

CYBER_DATA = [
    {"text": "Phishing attacks use fake emails to steal sensitive information.", "score": 0.98},
    {"text": "Ransomware encrypts data and demands payment for decryption keys.", "score": 0.95},
    {"text": "Multi-factor authentication helps prevent unauthorized access.", "score": 0.92},
    {"text": "Keep software updated to patch known vulnerabilities.", "score": 0.90},
    {"text": "Social engineering manipulates users into revealing confidential data.", "score": 0.89}
]

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify([])

    # Simple keyword search (replaceable with embeddings later)
    results = [item for item in CYBER_DATA if query in item["text"].lower()]
    return jsonify(results or [{"text": "No relevant cybersecurity info found.", "score": 0.0}])

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8002, debug=False)