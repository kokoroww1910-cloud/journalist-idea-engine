from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

from pipeline import fetch_news_signals, score_signals
from reasoning import generate_angles_and_keywords

app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/idea")
def idea():
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()

    if not topic:
        return jsonify({"error": "topic 不能为空"}), 400

    signals = fetch_news_signals(topic)
    scores = score_signals(signals)
    reasoning = generate_angles_and_keywords(topic, signals)

    return jsonify(
        {
            "topic": topic,
            "impact_score": scores["impact_score"],
            "potential_score": scores["potential_score"],
            "signals": signals,
            "angles": reasoning["angles"],
            "keywords": reasoning["keywords"],
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
