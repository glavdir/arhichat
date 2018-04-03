from yandex_translate import YandexTranslate
translate = YandexTranslate('trnsl.1.1.20140604T050552Z.5523a12a778f0bb8.7442f73f0140402650fe6aabd9d278a490f6da0c')

def to_eo(text):
    return text
    # return translate.translate(text,'be')['text'][0]
