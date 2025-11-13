from flask import Flask, request, jsonify
import re

app = Flask(__name__)

BREACHED_EMAILS = {
    "test@example.com": "Your email was found in a public data breach from 2021.",
    "admin@company.com": "Your email was found in a breach linked to leaked passwords."
}

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def check_breach(email: str) -> str:
    return BREACHED_EMAILS.get(email.lower(), "No breach found for this email.")

@app.route("/breach", methods=["GET"])
def breach_check():
    message = request.args.get("message", "")
    emails = re.findall(EMAIL_REGEX, message)
    if not emails:
        return jsonify({"response": "Please provide an email to check for breaches."})
    responses = [f"{email}: {check_breach(email)}" for email in emails]
    return jsonify({"response": "\n".join(responses)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001)