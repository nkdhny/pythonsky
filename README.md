# pytonsky

Питонский, Федор Михайлович.

Генератор всяческих текстов. Использует цепь маркова для генерации

## Структура

* `*.ipynb` - нотбуки с изысканиями на тему как заставить работать то или иное решение
* `pytonskiy.py` собственно питонсий
* `prazimov.md` плод творчества питонского

## Установка

Помимо обычных `requirements.txt` надо еще сделать

```python
import nltk
nltk.download()
```

Там надо выгрузить книгу, `book` (возможно и не надо вовсе, но с ней точно работает)

## Как работает

В сущности как и описано в условиях, но

* первое слово в предложении берет по распределению первых слов в предложении
* разбивает на параграфы имея распределение количества предложений, и считая, что предложение заканчивается после точки восклицательного знака или знака вопросаю
