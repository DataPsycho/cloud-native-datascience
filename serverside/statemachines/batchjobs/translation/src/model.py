import typing as t
from collections import namedtuple
from pathlib import Path
from src.logger import get_logger

from transformers import MarianMTModel, MarianTokenizer

ModelRepo = namedtuple("ModelRepo", "tokenizer, model")
DEFAULT_PATH = Path('lfs').joinpath('models', 'v0.0.1')
LOGGER = get_logger()


def load_mmt_artifacts(path: t.Optional[Path] = None) -> ModelRepo:
    """
    Loading the marian mt model objects from a given directory
    :param path: Directory path to load the files
    :return: Marian Model and Tokenizer tuple
    """
    path = path if path else DEFAULT_PATH
    model_repo = path.resolve().as_posix()
    try:
        LOGGER.info(f"Trying to load tokenizer from {model_repo}")
        tokenizer = MarianTokenizer.from_pretrained(model_repo)
        LOGGER.info(f"Trying to load model from {model_repo}")
        model = MarianMTModel.from_pretrained(model_repo)
        LOGGER.info("Model loaded from local path successfully.")
        return ModelRepo(tokenizer=tokenizer, model=model)
    except Exception as e:
        LOGGER.info(f"Can not load model from local path trying to download: Error {e}")
        try:
            model_name = "Helsinki-NLP/opus-mt-en-de"
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            LOGGER.info(f"Saving model and tokenizer at {path}")
            tokenizer.save_pretrained(path)
            model.save_pretrained(path)
            return ModelRepo(tokenizer=tokenizer, model=model)
        except Exception as e:
            LOGGER.info(f"Can not download model from source: {e}")
