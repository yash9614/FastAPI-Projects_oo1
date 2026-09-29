"""Optional CLI indexer. The API can do the same job via POST /index/."""

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from app.rag import DATA_DIR, index_pdf

DEFAULT_PDF = DATA_DIR / "sample.pdf"


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--replace"]
    replace = "--replace" in sys.argv
    pdf_path = Path(args[0]) if args else DEFAULT_PDF
    try:
        result = index_pdf(pdf_path, replace=replace)
    except (RuntimeError, FileNotFoundError) as exc:
        print(exc)
        sys.exit(1)

    print(
        f"Indexed {result['file']}: {result['pages']} page(s), "
        f"{result['chunks']} chunk(s) → {result['collection']}"
    )


if __name__ == "__main__":
    main()
