# 再翻訳くそあぷりです

## これは何？

これは、翻訳くそあぷりです。

## 使い方

`/re_translate`エンドポイントにGETリクエストを送信すると、再翻訳した文字列を取得できます。

| パラメータ  | 概要                              |
| ----------- | --------------------------------- |
| text        | 再翻訳したい文字列                |
| source_lang | `ja` など元の言語                 |
| via_langs   | `en,ru`など、カンマ区切りでの言語 |


### 例

```bash
$ curl -X GET "http://localhost:5000/re_translate?text=再翻訳くそあぷり&source_lang=ja&via_langs=en,ru"
```
