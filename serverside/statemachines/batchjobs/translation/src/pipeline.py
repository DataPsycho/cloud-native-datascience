import typing as t
from pathlib import Path

from src.doc_handler import create_document, read_document_to_paragraphs
from src.model import ModelRepo, load_mmt_artifacts


class Pipeline:
    def __init__(self, eng_file: Path, ger_file: Path, artifact_path: t.Optional[Path] = None):
        self.eng_file_path = eng_file
        self.artifacts: ModelRepo = load_mmt_artifacts(artifact_path)
        self.ger_fil_path = ger_file

    def translate(self, batch: list):
        translated = self.artifacts.model.generate(
            **self.artifacts.tokenizer(batch, return_tensors="pt", padding=True)
        )
        translated = [self.artifacts.tokenizer.decode(token, skip_special_tokens=True) for token in translated]
        return translated

    def execute(self):
        doc = read_document_to_paragraphs(self.eng_file_path)
        german_doc = {"title": None, "paragraphs": []}
        if doc.get("title"):
            title = self.translate([doc.get("title")])
            german_doc["title"] = ", ".join(title)
        for item in doc["paragraphs"]:
            batch = item.split(".")
            batch = [item.strip() for item in batch]
            result = self.translate(batch)
            result = ". ".join(result)
            german_doc["paragraphs"].append(result)
        create_document(german_doc, self.ger_fil_path)


if __name__ == "__main__":
    eng_file_path = Path("lfs").joinpath("documents", "demo.docx")
    ger_file_path = Path("lfs").joinpath("documents", "german_demo.docx")
    pipeline = Pipeline(eng_file_path, ger_file_path)
    pipeline.execute()


