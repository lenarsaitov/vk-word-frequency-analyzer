### Сбор и анализ частотности слов в постах и комментариях группы в вк

В данной работе собираются и анализируются слова, используемые при написании постов и комментариев к ним, 
на примере сообщества [Лентач](https://vk.com/lentach)

### Окружение
В проекте используется Python 3, также необходимы дополнительные библиотеки, такие как nltk, stop_words, pymorphy2, 
vk_api и т.д.

Для их установки используйте команду:

```
pip3 install -r requirements.txt
```

### Необходимые данные
Для использования данной работы, потребуется следующие данные:

* [login](https://vk-api.readthedocs.io/en/latest/) - логин от аккаунта в Вконтакте (желательно номер телефона)
* [password](https://vk-api.readthedocs.io/en/latest/) - пароль
* [owner_id](https://vk.com/dev/wall.get) - идентификатор сообщества (по умолчанию — Лентач)
* count_of_posts - количество постов, с которых собираются данные (по умолчанию — 500)

### Получаемые данные
В процессе выполнения, мы получаем

* frequency_post_words - частотность слов, используемые при написании постов
* frequency_main_comm_words - частотность слов, используемые при написании комментариев
* frequency_answ_comm_words - частотность слов, используемые при написании в ответах на комментарии

которые сохраняются в соответствующих трех файлах в папке results

### Структура работы
При помощи [специального API](https://vk.com/dev/api_requests) собираются данные с постов.

Далее убираются стоп-слова (предлоги, союзы, междометия, частицы и другие части речи, которые часто встречаются в 
тексте, являются служебными и не несут смысловой нагрузки, т.е. являются избыточными) и слова, не имеющие смысла (ссылки на что-либо, эмодзи итп) 

Затем используем морфологический анализ и приводим слова в первоначальную форму

Потом при помощи [nltk.probability](https://www.nltk.org/_modules/nltk/probability.html) уже определяется частотность этих слов

### Анализ полученных данных
В ноутбуке *research_results_data.ipynb* приводится первичный анализ полученных данных

Данные актуальны на *22.05.2021*