from pathlib import Path

import joblib
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
MODEL_FILE = ROOT / "models/document_classifier.joblib"


def extract_text(pdf_path):
    reader = PdfReader(str(pdf_path))

    return "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    ).strip()


def classify_pdf(pdf_path):
    pdf_path = Path(pdf_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    if not MODEL_FILE.exists():
        raise FileNotFoundError("Train the classifier first.")

    text = extract_text(pdf_path)

    if len(text) < 100:
        raise ValueError("Not enough extractable text in this PDF.")

    model = joblib.load(MODEL_FILE)

    prediction = model.predict([text])[0]

    scores = model.predict_proba([text])[0]
    score_by_category = dict(
        zip(model.classes_, scores)
    )

    return {
        "filename": pdf_path.name,
        "category": prediction,
        "scores": score_by_category,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m src.classifier.predict path/to/file.pdf")
        raise SystemExit(1)

    result = classify_pdf(sys.argv[1])

    print("\n===== DOCUMENT CLASSIFICATION =====")
    print("File:", result["filename"])
    print("Predicted category:", result["category"])
    print("\nModel scores:")

    for category, score in result["scores"].items():
        print(f"{category}: {score:.3f}")
