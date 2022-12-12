from transformers import MarianMTModel, MarianTokenizer
import logging
from collections import namedtuple

ModelRepo = namedtuple("ModelRepo", "tokenizer, model")


def load_download_model() -> ModelRepo:
    """Download or load model from local path"""
    model_name = "Helsinki-NLP/opus-mt-en-de"
    local_path = "lfs/models/v0.0.1"
    try:
        tokenizer = MarianTokenizer.from_pretrained(local_path)
        model = MarianMTModel.from_pretrained(local_path)
        logging.info("Loading model from local path.")
        return ModelRepo(tokenizer=tokenizer, model=model)
    except Exception as e:
        logging.info(f"Can not load model from local path trying to download: {e}")
        try:
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            tokenizer.save_pretrained(local_path)
            model.save_pretrained(local_path)
            return ModelRepo(tokenizer=tokenizer, model=model)
        except Exception as e:
            logging.info(f"Can not download model from source: {e}")


def test_translation(model_repo: ModelRepo) -> list:
    src_texts = ["I am a small frog.", "Tom asked his teacher for advice."]
    tgt_texts = ["Ich bin ein kleiner Frosch.", "Tom bat seinen Lehrer um Rat."]  # optional
    translated = model_repo.model.generate(
        **model_repo.tokenizer(src_texts, return_tensors="pt", padding=True)
    )
    translated = [model_repo.tokenizer.decode(t, skip_special_tokens=True, max_new_token=512) for t in translated]
    assert tgt_texts == translated
    return translated


if __name__ == "__main__":
    model_pipeline = load_download_model()
    translation = test_translation(model_pipeline)
    print(translation)

