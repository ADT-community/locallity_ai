import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from urllib import request, parse


def load_questions(path: Path):
    """Load questions from a JSON file.

    Expected format:
    [
        {"id": "q1", "question": "What is ...?"},
        ...
    ]
    """
    if not path.is_file():
        raise FileNotFoundError(f"Question file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Question file must contain a JSON array")
    return data


def call_api(api_url: str, question: str):
    """Send a single question to the API and return the raw response string.

    The API is expected to accept a JSON payload ``{"question": "..."}`` via POST
    and return a JSON object containing at least a ``"answer"`` field.
    """
    payload = json.dumps({"question": question}).encode("utf-8")
    req = request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as resp:
        resp_data = resp.read().decode("utf-8")
    try:
        resp_json = json.loads(resp_data)
        # Prefer a top‑level "answer" field, otherwise return the whole payload
        return resp_json.get("answer", resp_json)
    except json.JSONDecodeError:
        # If the API returns plain text, just return it
        return resp_data


def score_reply(reply) -> int:
    """Very simple rubric: 1 if the reply is non‑empty after stripping, else 0.

    This placeholder can be swapped out for a more sophisticated LLM judge.
    """
    if isinstance(reply, dict):
        # If the reply is a dict, convert to string for the simple check
        reply_str = json.dumps(reply)
    else:
        reply_str = str(reply)
    return 1 if reply_str.strip() else 0


def main():
    parser = argparse.ArgumentParser(description="Evaluate an API against a set of questions.")
    parser.add_argument("--api", required=True, help="Base URL of the API to evaluate (e.g., http://localhost:8000/api)")
    parser.add_argument(
        "--questions",
        default=str(Path(__file__).parent / "questions.json"),
        help="Path to the JSON file containing the question set.",
    )
    args = parser.parse_args()

    questions_path = Path(args.questions)
    questions = load_questions(questions_path)

    results = []
    total_score = 0

    for entry in questions:
        q_id = entry.get("id", "unknown")
        question_text = entry.get("question", "")
        try:
            reply = call_api(args.api, question_text)
        except Exception as e:
            reply = f"<error: {e}>"
        score = score_reply(reply)
        total_score += score
        results.append({
            "id": q_id,
            "question": question_text,
            "reply": reply,
            "score": score,
        })

    # Compute overall percentage
    overall_pct = (total_score / len(questions)) * 100 if questions else 0.0
    print(f"Processed {len(questions)} questions.")
    print(f"Score: {overall_pct:.2f}% ({total_score}/{len(questions)})")

    # Save results with timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    results_dir = Path(__file__).parent / "results"
    os.makedirs(results_dir, exist_ok=True)
    results_path = results_dir / f"{timestamp}.json"
    with results_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
