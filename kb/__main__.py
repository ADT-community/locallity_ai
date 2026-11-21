"""Command line helpers: build the index, search it, or regenerate evaluation results."""

import argparse
import json

from . import evaluate, ingest, store
from .search import KnowledgeBase


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m kb")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="build and save the embedding index")
    build.add_argument("--backend", default="hashing")
    search_parser = commands.add_parser("search", help="search the knowledge base")
    search_parser.add_argument("question")
    search_parser.add_argument("-k", type=int, default=5)
    commands.add_parser("eval", help="regenerate retrieval evidence for 10 questions")
    args = parser.parse_args(argv)

    if args.command == "build":
        backend = ingest.get_backend(args.backend) if args.backend != "hashing" else None
        index = ingest.build_index(backend=backend)
        path = store.save_index(index)
        print("Indexed %d chunks from %d sources -> %s" % (
            len(index["documents"]), len({d["id"] for d in index["documents"]}), path))
    elif args.command == "search":
        kb = KnowledgeBase(store.ensure_index())
        for rank, result in enumerate(kb.search(args.question, k=args.k), 1):
            print("%d. [%.4f] %s (%s)\n   %s\n   %s" % (
                rank, result["score"], result["title"], result["url"],
                result["passage"][:160], result["license"]))
    else:
        path = evaluate.write_results()
        print("Wrote %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
