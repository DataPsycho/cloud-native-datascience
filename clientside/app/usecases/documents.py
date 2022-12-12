import logging
from collections import namedtuple

from app.domains.document import (GetDocumentStatusPayload,
                                  GetGermanDocumentPayload,
                                  PostEnglishDocPayload)
from app.domains.jobs import TranslationJob
from app.domains.project import Project
from app.usecases import CLIENT
from app.usecases.exceptions import UseCaseConversionException

GermanDocResult = namedtuple("GermanDocResult", "content, query")


def get_german_document(payload: GetGermanDocumentPayload) -> GermanDocResult:
    path = "documents/german"
    result = CLIENT.get(path=path, query=payload.dict())
    if result.success:
        content = result.data["content"]
        query = TranslationJob(**result.data["query"])
        return GermanDocResult(content, query)
    logging.info(result.trace)
    raise UseCaseConversionException(result.trace)


def confirm_english_document(payload: GetDocumentStatusPayload) -> bool:
    path = "documents/english/added"
    result = CLIENT.get(path=path, query=payload.dict())
    if result.success:
        return result.data["added"]
    raise UseCaseConversionException(result.trace)


def save_english_document(payload: PostEnglishDocPayload) -> Project:
    path = "documents/english"
    result = CLIENT.post(path=path, body=payload.json())
    if result.success:
        return Project(**result.data)
    logging.info(result.trace)
    raise UseCaseConversionException(result.trace)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from xfilios.docx import DocxHandler, ReadDocFunc
    load_dotenv()
    import os
    _payload = GetGermanDocumentPayload(pid=os.environ["TEMP_PROJECT_NAME"])
    get_german_document(_payload)
    _payload = GetDocumentStatusPayload(pid=os.environ["TEMP_PROJECT_NAME"])
    confirm_english_document(_payload)
    doc_file = ReadDocFunc("lfs/documents/english-demo.docx")
    handler = DocxHandler(document=doc_file, name="english-demo.docx")
    _payload = PostEnglishDocPayload(
        sk=os.environ["TEMP_PROJECT_NAME"],
        doc=handler.name,
        data=handler.to_base64_str()
    )

    # path = "documents/english"
    # result = CLIENT.post(path=path, body=_payload.dict())

