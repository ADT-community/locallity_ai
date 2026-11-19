import pytest
from api.search import search

# Ten representative farming questions (feel free to extend)
TEST_QUESTIONS = [
    "What is the best time to plant corn in the Midwest?",
    "How can I control aphids on lettuce without chemicals?",
    "What soil pH is optimal for blueberries?",
    "How do I prevent powdery mildew on tomatoes?",
    "What are the water requirements for rice paddies?",
    "Which cover crops improve nitrogen for corn?",
    "How to store harvested potatoes to avoid sprouting?",
    "What organic fertilizer works best for strawberries?",
    "How to identify and treat fusarium wilt in beans?",
    "What is the recommended rotation schedule for wheat and legumes?",
]


def test_search_returns_results():
    for q in TEST_QUESTIONS:
        results = search(q, k=5)
        # Ensure we get exactly k results
        assert len(results) == 5, f"Expected 5 results for '{q}', got {len(results)}"
        # Each result must contain required keys
        for r in results:
            assert "passage" in r and r["passage"], "Missing passage text"
            assert "source" in r and r["source"], "Missing source name"
            assert "url" in r and r["url"], "Missing source URL"
            assert "score" in r and isinstance(r["score"], float), "Missing or invalid score"
        # Optional: print for manual inspection (pytest captures output)
        print(f"\nQuestion: {q}\nTop passages:")
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r['source']}]({r['url']}) – Score: {r['score']:.4f}\n   {r['passage'][:200]}...")
