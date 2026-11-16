from pathlib import Path

import pandas as pd
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]

LABELS_FILE = PROJECT_ROOT / "data/training/labels.csv"
PDF_FOLDER = PROJECT_ROOT / "data/training/pdfs"
OUTPUT_FILE = PROJECT_ROOT / "data/training/processed_documents.csv"

VALID_CATEGORIES = {
    "academic",
    "technical",
    "business",
    "administrative",
    "legal",
}


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from all pages of a PDF."""
    reader = PdfReader(str(pdf_path))

    pages = [
        page.extract_text() or ""
        for page in reader.pages
    ]

    return "\n".join(pages).strip()


def prepare_dataset() -> pd.DataFrame:
    """Build a labelled dataset from the PDF files."""

    if not LABELS_FILE.exists():
        raise FileNotFoundError(f"Labels file not found: {LABELS_FILE}")

    labels = pd.read_csv(LABELS_FILE)

    required_columns = {"filename", "category"}

    if not required_columns.issubset(labels.columns):
        raise ValueError(
            "labels.csv must contain filename and category columns."
        )

    if labels.empty:
        raise ValueError("The labels file contains no documents.")

    if labels["filename"].duplicated().any():
        raise ValueError("Duplicate filenames found in labels.csv.")

    records = []

    for _, row in labels.iterrows():
        filename = str(row["filename"]).strip()
        category = str(row["category"]).strip().lower()

        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}' for {filename}."
            )

        pdf_path = PDF_FOLDER / filename

        if not pdf_path.is_file():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        text = extract_pdf_text(pdf_path)

        if len(text) < 100:
            raise ValueError(
                f"Insufficient extractable text in {filename}: "
                f"{len(text)} characters."
            )

        records.append({
            "filename": filename,
            "category": category,
            "text": text,
            "character_count": len(text),
        })

    dataset = pd.DataFrame(records)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(OUTPUT_FILE, index=False)

    return dataset


if __name__ == "__main__":
    df = prepare_dataset()

    print("\n===== DATASET PREPARATION =====")
    print(f"Documents prepared: {len(df)}")
    print(f"Total extracted characters: {df['character_count'].sum()}")

    print("\n===== CATEGORY DISTRIBUTION =====")
    print(df["category"].value_counts().to_string())

    print(f"\nDataset saved to: {OUTPUT_FILE}")
