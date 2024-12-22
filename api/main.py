from argostranslate import translate
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from functools import lru_cache
from typing import List

app = FastAPI()


@lru_cache(2 ** 10)
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    translated_text = translate.translate(
        text,
        source_lang,
        target_lang
    )
    return translated_text


def re_translate_text(text: str, source_lang: str, via_langs: List[str]) -> str:
    # 元の言語から中間言語へ翻訳
    translated_text = translate_text(
        text,
        source_lang,
        via_langs[0]
    )

    # 中間言語から中間言語へ翻訳
    for i in range(len(via_langs) - 1):
        translated_text = translate_text(
            translated_text,
            via_langs[i],
            via_langs[i + 1]
        )

    # 中間言語から元の言語へ翻訳
    translated_text = translate_text(
        translated_text,
        via_langs[-1],
        source_lang
    )
    return translated_text


@app.get("/re_translate")
def re_translate(text: str, source_lang: str, via_langs: str):
    """再翻訳して人間が理解できないテキストに翻訳します。
    """
    return PlainTextResponse(
        re_translate_text(
            text,
            source_lang,
            via_langs.split(",")))
