# Простой перевод
hello = Привет, мир!

# Многострочное значение
multiline =
    Это многострочное сообщение.
    Оно продолжается на нескольких строках.

# Переменные
welcome = Привет, { $name }!

# Атрибуты
button =
    .label = Отправить
    .accesskey = O

# Варианты (селекторы)
email-status =
    { $unreadCount ->
        [0] У вас нет новых писем.
        [one] У вас { $unreadCount } новое письмо.
        [few] У вас { $unreadCount } новых письма.
       *[other] У вас { $unreadCount } новых писем.
    }

# Использование другого сообщения (message reference)
greeting = { hello } Это фраза с другим сообщением.

# Селектор по состоянию
task-state =
    { $state ->
        [new] Новая задача
        [in-progress] В процессе
        [done] Завершена
       *[other] Неизвестное состояние
    }

# Вызов функций (например, для форматирования даты/чисел)
formatted-date = Сегодня: { DATETIME($date, month: "long", year: "numeric", day: "numeric") }

# Пример с NUMBER и использование параметров
score = Вы набрали { NUMBER($points, minimumFractionDigits: 1) } очков

# Пример с вложенными сообщениями
outer-message = Вложение: { inner-message }
inner-message = Это вложенное сообщение.

# Escaping фигурных скобок
escaped = Это не переменная: {{ $notAVar }}

# Использование term-ов (терминов, начинающихся с -)
-brand-name = Приложение X
about = Информация о { -brand-name }

# Атрибут у термина
-icon =
    .src = /images/icon.svg
    .alt = Иконка

# Комментарии
# Это обычный комментарий
## Это групповой комментарий
### Это документирующий комментарий

# Комбинация всего
complex-message =
    Добро пожаловать, { $name }!
    Сегодня { DATETIME($date, weekday: "long") }.
    У вас { $unreadCount ->
        [0] нет новых писем.
        [one] одно новое письмо.
        [few] { $unreadCount } новых письма.
       *[other] { $unreadCount } новых писем.
    }
    Спасибо, что используете { -brand-name }!