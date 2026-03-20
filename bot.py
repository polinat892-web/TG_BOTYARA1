import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==================== НАСТРОЙКИ ====================
TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

# Хранилище ответов пользователей
user_data = {}

# ==================== ТЕСТ ТОМАСА-КИЛМАННА (30 вопросов) ====================
THOMAS_QUESTIONS = [
    {"text": "Когда возникает конфликт, я обычно...", "options": ["Настаиваю на своем решении", "Стараюсь найти решение, которое устроит всех"], "scores": ["COMPETING", "COLLABORATING"]},
    {"text": "Если коллега не согласен с моим предложением, я...", "options": ["Предлагаю найти золотую середину", "Предлагаю отложить обсуждение на потом"], "scores": ["COMPROMISING", "AVOIDING"]},
    {"text": "Когда конфликт затрагивает важные для меня вопросы, я...", "options": ["Борюсь за свои интересы до конца", "Иду на уступки, чтобы сохранить отношения"], "scores": ["COMPETING", "ACCOMMODATING"]},
    {"text": "В споре с близким человеком я обычно...", "options": ["Стараюсь понять его точку зрения и найти общее решение", "Предлагаю обоим немного уступить"], "scores": ["COLLABORATING", "COMPROMISING"]},
    {"text": "Если начальник дает невыполнимое задание, я...", "options": ["Молча выполняю, как могу", "Избегаю обсуждения этого вопроса"], "scores": ["ACCOMMODATING", "AVOIDING"]},
    {"text": "Когда в команде возникают разногласия, я...", "options": ["Предлагаю обсудить все мнения и прийти к консенсусу", "Настаиваю на своем варианте как наиболее правильном"], "scores": ["COLLABORATING", "COMPETING"]},
    {"text": "Если партнер по проекту не выполняет свою часть работы, я...", "options": ["Говорю, что сделаю его часть, чтобы проект не пострадал", "Предлагаю разделить работу по-другому"], "scores": ["ACCOMMODATING", "COMPROMISING"]},
    {"text": "Когда спор становится слишком эмоциональным, я...", "options": ["Предлагаю сделать перерыв и вернуться к обсуждению позже", "Стараюсь успокоить всех и найти компромисс"], "scores": ["AVOIDING", "COMPROMISING"]},
    {"text": "Если мое мнение не учитывают при принятии решения, я...", "options": ["Настойчиво требую, чтобы мое мнение было услышано", "Стараюсь доказать свою правоту с помощью фактов и логики"], "scores": ["COMPETING", "COLLABORATING"]},
    {"text": "Когда конфликт не принципиален для меня, я...", "options": ["Легко соглашаюсь с другим человеком", "Избегаю дальнейшего обсуждения"], "scores": ["ACCOMMODATING", "AVOIDING"]},
    {"text": "В конфликте с подчиненным я...", "options": ["Требую выполнения моих указаний без возражений", "Стараюсь объяснить свою позицию и выслушать его"], "scores": ["COMPETING", "COLLABORATING"]},
    {"text": "Если друзья спорят, я...", "options": ["Предлагаю каждому немного уступить", "Стараюсь их помирить, найдя общее решение"], "scores": ["COMPROMISING", "COLLABORATING"]},
    {"text": "Когда меня критикуют незаслуженно, я...", "options": ["Молча принимаю критику, чтобы не усугублять ситуацию", "Избегаю дальнейшего общения с этим человеком"], "scores": ["ACCOMMODATING", "AVOIDING"]},
    {"text": "В переговорах я обычно...", "options": ["Стараюсь добиться максимальной выгоды для себя", "Ищу вариант, где обе стороны получат что-то важное"], "scores": ["COMPETING", "COLLABORATING"]},
    {"text": "Если коллега постоянно перебивает меня на совещаниях, я...", "options": ["Терпеливо жду, когда он закончит", "Предлагаю установить правила выступления"], "scores": ["ACCOMMODATING", "COMPROMISING"]},
    {"text": "Когда проект находится под угрозой из-за разногласий в команде, я...", "options": ["Беру руководство на себя и принимаю решение единолично", "Организую мозговой штурм для поиска лучшего решения"], "scores": ["COMPETING", "COLLABORATING"]},
    {"text": "Если супруг(а) хочет провести отпуск не там, где хочу я, я...", "options": ["Предлагаю разделить отпуск или выбрать нейтральное место", "Соглашаюсь с его(ее) выбором, чтобы избежать ссоры"], "scores": ["COMPROMISING", "ACCOMMODATING"]},
    {"text": "Когда начальник неправ, но настаивает на своем, я...", "options": ["Молча выполняю указания, даже если не согласен", "Стараюсь мягко предложить альтернативу"], "scores": ["ACCOMMODATING", "COLLABORATING"]},
    {"text": "В конфликте из-за ресурсов на работе я...", "options": ["Требую свою долю, аргументируя потребностями", "Предлагаю поделить ресурсы поровну"], "scores": ["COMPETING", "COMPROMISING"]},
    {"text": "Если меня обвиняют в чем-то, чего я не делал, я...", "options": ["Резко отвергаю обвинения и защищаюсь", "Спокойно предлагаю разобраться в ситуации вместе"], "scores": ["COMPETING", "COLLABORATING"]},
    {"text": "Когда сроки горят, а команда не может договориться, я...", "options": ["Принимаю решение сам и требую выполнения", "Предлагаю временное решение, чтобы успеть в срок"], "scores": ["COMPETING", "COMPROMISING"]},
    {"text": "Если друг постоянно опаздывает на встречи, я...", "options": ["Молча терплю, чтобы не портить отношения", "Перестаю назначать встречи заранее"], "scores": ["ACCOMMODATING", "AVOIDING"]},
    {"text": "В споре о политике или религии я...", "options": ["Избегаю таких тем в разговоре", "Стараюсь найти точки соприкосновения"], "scores": ["AVOIDING", "COLLABORATING"]},
    {"text": "Когда клиент недоволен, но его требования нереалистичны, я...", "options": ["Предлагаю частичное удовлетворение требований", "Объясняю, почему требования невыполнимы, и ищу альтернативу"], "scores": ["COMPROMISING", "COLLABORATING"]},
    {"text": "Если коллега присваивает себе мои идеи, я...", "options": ["Прямо заявляю о своем авторстве при всех", "Говорю с ним наедине о ситуации"], "scores": ["COMPETING", "COLLABORATING"]},
    {"text": "Когда в семье спорят о распределении обязанностей, я...", "options": ["Предлагаю составить график дежурств", "Беру на себя больше, чтобы избежать конфликтов"], "scores": ["COMPROMISING", "ACCOMMODATING"]},
    {"text": "Если проектная группа не может выбрать технологию, я...", "options": ["Предлагаю протестировать несколько вариантов", "Настаиваю на той технологии, в которой лучше разбираюсь"], "scores": ["COLLABORATING", "COMPETING"]},
    {"text": "Когда меня перебивают в важном разговоре, я...", "options": ["Терпеливо жду своей очереди", "Вежливо, но твердо продолжаю говорить"], "scores": ["ACCOMMODATING", "COMPETING"]},
    {"text": "Если команда не может согласовать дизайн проекта, я...", "options": ["Предлагаю проголосовать за лучший вариант", "Объединяю элементы из разных предложений"], "scores": ["COMPROMISING", "COLLABORATING"]},
    {"text": "Когда конфликт угрожает дедлайну, я...", "options": ["Предлагаю быстро принять компромиссное решение", "Настаиваю на правильном решении, даже если это займет время"], "scores": ["COMPROMISING", "COMPETING"]}
]

# ==================== ТЕСТ КЕЙРСИ (70 вопросов) ====================
KEIRSEY_QUESTIONS = [
    {"text": "В компании я обычно:", "options": ["Наблюдаю и слушаю", "Активно общаюсь"], "scores": ["SP", "NF"]},
    {"text": "При принятии решений я больше полагаюсь на:", "options": ["Логику и факты", "Чувства и эмоции"], "scores": ["NT", "NF"]},
    {"text": "Я предпочитаю:", "options": ["Планировать заранее", "Действовать спонтанно"], "scores": ["SJ", "SP"]},
    {"text": "Для меня важнее:", "options": ["Сохранение традиций", "Инновации и изменения"], "scores": ["SJ", "NT"]},
    {"text": "В работе я ценю:", "options": ["Стабильность и порядок", "Свободу и гибкость"], "scores": ["SJ", "SP"]},
    {"text": "Я скорее:", "options": ["Реалист и практик", "Мечтатель и идеалист"], "scores": ["SP", "NF"]},
    {"text": "В общении я:", "options": ["Прямолинеен и честен", "Тактичен и дипломатичен"], "scores": ["NT", "NF"]},
    {"text": "Мне нравится:", "options": ["Следовать правилам", "Находить обходные пути"], "scores": ["SJ", "SP"]},
    {"text": "Я больше интересуюсь:", "options": ["Конкретными фактами", "Теориями и идеями"], "scores": ["SJ", "NT"]},
    {"text": "В сложной ситуации я:", "options": ["Сохраняю спокойствие", "Проявляю эмоции"], "scores": ["NT", "NF"]},
    {"text": "Я предпочитаю:", "options": ["Известное и проверенное", "Новое и неизведанное"], "scores": ["SJ", "NT"]},
    {"text": "Для меня важнее:", "options": ["Справедливость", "Гармония"], "scores": ["NT", "NF"]},
    {"text": "Я скорее:", "options": ["Осторожный и осмотрительный", "Рисковый и смелый"], "scores": ["SJ", "SP"]},
    {"text": "В обучении я предпочитаю:", "options": ["Практический опыт", "Теоретические знания"], "scores": ["SP", "NT"]},
    {"text": "Я ценю в людях:", "options": ["Надежность и ответственность", "Креативность и воображение"], "scores": ["SJ", "NF"]},
    {"text": "Мой подход к жизни:", "options": ["Серьезный и ответственный", "Легкий и спонтанный"], "scores": ["SJ", "SP"]},
    {"text": "Я больше ориентирован на:", "options": ["Настоящее", "Будущее"], "scores": ["SP", "NT"]},
    {"text": "В конфликте я стремлюсь:", "options": ["Установить истину", "Сохранить отношения"], "scores": ["NT", "NF"]},
    {"text": "Я предпочитаю работу:", "options": ["Структурированную и четкую", "Свободную и творческую"], "scores": ["SJ", "NF"]},
    {"text": "Мне важнее:", "options": ["Эффективность", "Эстетика"], "scores": ["NT", "NF"]},
    {"text": "Я скорее:", "options": ["Традиционалист", "Новатор"], "scores": ["SJ", "NT"]},
    {"text": "В свободное время я предпочитаю:", "options": ["Активный отдых", "Спокойные занятия"], "scores": ["SP", "SJ"]},
    {"text": "Я больше доверяю:", "options": ["Опыту", "Интуиции"], "scores": ["SJ", "NF"]},
    {"text": "При принятии решений я:", "options": ["Взвешиваю все за и против", "Доверяю внутреннему голосу"], "scores": ["NT", "NF"]},
    {"text": "Я ценю в себе:", "options": ["Практичность", "Творчество"], "scores": ["SP", "NF"]},
    {"text": "Мне комфортнее:", "options": ["В одиночестве", "В компании"], "scores": ["NT", "NF"]},
    {"text": "Я предпочитаю:", "options": ["Конкретные инструкции", "Общие указания"], "scores": ["SJ", "NT"]},
    {"text": "Для меня важнее:", "options": ["Факты", "Возможности"], "scores": ["SJ", "NT"]},
    {"text": "Я скорее:", "options": ["Реалист", "Идеалист"], "scores": ["SP", "NF"]},
    {"text": "В отношениях я ценю:", "options": ["Стабильность", "Страсть"], "scores": ["SJ", "SP"]},
    {"text": "Я предпочитаю:", "options": ["Избегать конфликтов", "Решать проблемы открыто"], "scores": ["NF", "NT"]},
    {"text": "Мне важнее:", "options": ["Быть полезным", "Быть уникальным"], "scores": ["SJ", "NF"]},
    {"text": "Я скорее:", "options": ["Терпеливый", "Нетерпеливый"], "scores": ["SJ", "SP"]},
    {"text": "В работе я предпочитаю:", "options": ["Закончить одно дело", "Работать над несколькими"], "scores": ["SJ", "SP"]},
    {"text": "Я больше ориентирован на:", "options": ["Процесс", "Результат"], "scores": ["SP", "NT"]},
    {"text": "Мне нравится:", "options": ["Следовать плану", "Импровизировать"], "scores": ["SJ", "SP"]},
    {"text": "Я ценю в информации:", "options": ["Точность", "Интересность"], "scores": ["NT", "NF"]},
    {"text": "Я скорее:", "options": ["Консервативный", "Либеральный"], "scores": ["SJ", "NT"]},
    {"text": "Для меня важнее:", "options": ["Быть правым", "Быть понятым"], "scores": ["NT", "NF"]},
    {"text": "Я предпочитаю:", "options": ["Рутинную работу", "Разнообразные задачи"], "scores": ["SJ", "SP"]},
    {"text": "Мне комфортнее:", "options": ["В знакомой обстановке", "В новых ситуациях"], "scores": ["SJ", "SP"]},
    {"text": "Я больше доверяю:", "options": ["Статистике", "Личному опыту"], "scores": ["NT", "NF"]},
    {"text": "Я скорее:", "options": ["Организованный", "Гибкий"], "scores": ["SJ", "SP"]},
    {"text": "Для меня важнее:", "options": ["Здравый смысл", "Воображение"], "scores": ["SP", "NF"]},
    {"text": "Я предпочитаю:", "options": ["Прямые ответы", "Дипломатичные ответы"], "scores": ["NT", "NF"]},
    {"text": "Мне важнее:", "options": ["Содержание", "Форма"], "scores": ["NT", "NF"]},
    {"text": "Я скорее:", "options": ["Последовательный", "Спонтанный"], "scores": ["SJ", "SP"]},
    {"text": "В обучении я предпочитаю:", "options": ["Структурированные курсы", "Самостоятельное изучение"], "scores": ["SJ", "NT"]},
    {"text": "Я ценю в работе:", "options": ["Стабильность", "Возможности для роста"], "scores": ["SJ", "NT"]},
    {"text": "Мой стиль общения:", "options": ["Формальный", "Неформальный"], "scores": ["SJ", "SP"]},
    {"text": "Я скорее:", "options": ["Осторожный в высказываниях", "Откровенный"], "scores": ["NF", "NT"]},
    {"text": "Для меня важнее:", "options": ["Фактическая правда", "Эмоциональная правда"], "scores": ["NT", "NF"]},
    {"text": "Я предпочитаю:", "options": ["Избегать ошибок", "Экспериментировать"], "scores": ["SJ", "SP"]},
    {"text": "Мне комфортнее:", "options": ["С четкими инструкциями", "С свободой действий"], "scores": ["SJ", "NT"]},
    {"text": "Я скорее:", "options": ["Реалистичный в целях", "Амбициозный"], "scores": ["SP", "NT"]},
    {"text": "Для меня важнее:", "options": ["Процедуры", "Результаты"], "scores": ["SJ", "NT"]},
    {"text": "Я предпочитаю:", "options": ["Работать в одиночку", "Работать в команде"], "scores": ["NT", "NF"]},
    {"text": "Мне важнее:", "options": ["Быть компетентным", "Быть любимым"], "scores": ["NT", "NF"]},
    {"text": "Я скорее:", "options": ["Прагматик", "Мечтатель"], "scores": ["SP", "NF"]},
    {"text": "В принятии решений я:", "options": ["Медленный и обдуманный", "Быстрый и решительный"], "scores": ["SJ", "SP"]},
    {"text": "Я ценю в себе:", "options": ["Надежность", "Оригинальность"], "scores": ["SJ", "NF"]},
    {"text": "Мне важнее:", "options": ["Соответствовать стандартам", "Выделяться из толпы"], "scores": ["SJ", "NF"]},
    {"text": "Я скорее:", "options": ["Осторожный с деньгами", "Щедрый"], "scores": ["SJ", "NF"]},
    {"text": "Я предпочитаю:", "options": ["Известные маршруты", "Новые пути"], "scores": ["SJ", "SP"]},
    {"text": "Мне комфортнее:", "options": ["В структурированной среде", "В хаотичной среде"], "scores": ["SJ", "SP"]},
    {"text": "Я скорее:", "options": ["Последовательный в привычках", "Разнообразный в интересах"], "scores": ["SJ", "SP"]},
    {"text": "Для меня важнее:", "options": ["Закончить начатое", "Начать новое"], "scores": ["SJ", "SP"]},
    {"text": "Я предпочитаю:", "options": ["Детальные описания", "Общие концепции"], "scores": ["SJ", "NT"]},
    {"text": "Мне важнее:", "options": ["Практическая польза", "Теоретическая ценность"], "scores": ["SP", "NT"]},
    {"text": "Я скорее:", "options": ["Терпимый к рутине", "Ищущий новизны"], "scores": ["SJ", "SP"]}
]

# ==================== МОТИВАЦИОННЫЙ ТЕСТ (50 вопросов) ====================
MOTIVATION_QUESTIONS = [
    {"text": "Мне важно постоянно совершенствовать свои навыки и умения.", "category": "ACHIEVEMENT"},
    {"text": "Я ставлю перед собой амбициозные цели и стремлюсь их достичь.", "category": "ACHIEVEMENT"},
    {"text": "Мне нравится браться за сложные задачи, которые требуют максимум усилий.", "category": "ACHIEVEMENT"},
    {"text": "Я получаю удовольствие от решения трудных проблем.", "category": "ACHIEVEMENT"},
    {"text": "Для меня важно быть лучшим в том, чем я занимаюсь.", "category": "ACHIEVEMENT"},
    {"text": "Я стремлюсь к профессиональному росту и развитию.", "category": "ACHIEVEMENT"},
    {"text": "Мне важно видеть конкретные результаты своей работы.", "category": "ACHIEVEMENT"},
    {"text": "Я часто сравниваю свои достижения с достижениями других.", "category": "ACHIEVEMENT"},
    {"text": "Невыполненная задача вызывает у меня дискомфорт.", "category": "ACHIEVEMENT"},
    {"text": "Я готов много работать ради достижения успеха.", "category": "ACHIEVEMENT"},
    {"text": "Мне нравится брать на себя ответственность за других людей.", "category": "POWER"},
    {"text": "Я чувствую себя комфортно, когда руковожу проектом или командой.", "category": "POWER"},
    {"text": "Мне важно иметь возможность влиять на решения других.", "category": "POWER"},
    {"text": "Я получаю удовольствие от того, что могу контролировать ситуацию.", "category": "POWER"},
    {"text": "Мне нравится убеждать других в своей точке зрения.", "category": "POWER"},
    {"text": "Я стремлюсь к положению, которое дает власть и авторитет.", "category": "POWER"},
    {"text": "Мне важно, чтобы мои указания выполнялись без возражений.", "category": "POWER"},
    {"text": "Я чувствую себя увереннее, когда руковожу процессом.", "category": "POWER"},
    {"text": "Мне нравится организовывать работу других людей.", "category": "POWER"},
    {"text": "Я стремлюсь к позиции, где можно принимать важные решения.", "category": "POWER"},
    {"text": "Для меня важно иметь хорошие отношения с коллегами.", "category": "AFFILIATION"},
    {"text": "Я ценю теплую и дружескую атмосферу на работе.", "category": "AFFILIATION"},
    {"text": "Мне нравится работать в команде, а не в одиночку.", "category": "AFFILIATION"},
    {"text": "Я стремлюсь быть частью коллектива, чувствовать принадлежность.", "category": "AFFILIATION"},
    {"text": "Для меня важно поддерживать контакты с людьми вне работы.", "category": "AFFILIATION"},
    {"text": "Я избегаю конфликтов и стремлюсь к гармонии в отношениях.", "category": "AFFILIATION"},
    {"text": "Мне нравится помогать другим и чувствовать себя полезным.", "category": "AFFILIATION"},
    {"text": "Я ценю сотрудничество больше, чем конкуренцию.", "category": "AFFILIATION"},
    {"text": "Одиночество на работе вызывает у меня дискомфорт.", "category": "AFFILIATION"},
    {"text": "Мне важно чувствовать себя принятым в коллективе.", "category": "AFFILIATION"},
    {"text": "Мне важно, чтобы другие ценили мои заслуги.", "category": "RECOGNITION"},
    {"text": "Я хочу, чтобы мои успехи были заметны окружающим.", "category": "RECOGNITION"},
    {"text": "Похвала и благодарность мотивируют меня работать лучше.", "category": "RECOGNITION"},
    {"text": "Мне нравится, когда меня публично отмечают за хорошую работу.", "category": "RECOGNITION"},
    {"text": "Я стремлюсь к позициям, которые приносят уважение и почет.", "category": "RECOGNITION"},
    {"text": "Для меня важно иметь статус и репутацию в профессиональной среде.", "category": "RECOGNITION"},
    {"text": "Мне приятно, когда другие обращаются ко мне за советом.", "category": "RECOGNITION"},
    {"text": "Я ценю официальные награды и знаки отличия.", "category": "RECOGNITION"},
    {"text": "Мне важно, чтобы мой вклад в общее дело был замечен.", "category": "RECOGNITION"},
    {"text": "Я стремлюсь к тому, чтобы мое имя было известно в профессиональных кругах.", "category": "RECOGNITION"},
    {"text": "Для меня важна стабильность и предсказуемость на работе.", "category": "SECURITY"},
    {"text": "Я предпочитаю ясные инструкции и четкие правила.", "category": "SECURITY"},
    {"text": "Мне важно иметь гарантированную работу и стабильный доход.", "category": "SECURITY"},
    {"text": "Я избегаю ситуаций с неопределенностью и риском.", "category": "SECURITY"},
    {"text": "Для меня важны социальные гарантии и пенсионное обеспечение.", "category": "SECURITY"},
    {"text": "Я предпочитаю работать в надежной и проверенной компании.", "category": "SECURITY"},
    {"text": "Мне комфортнее в структурированной и организованной среде.", "category": "SECURITY"},
    {"text": "Я ценю долгосрочные контракты и постоянную занятость.", "category": "SECURITY"},
    {"text": "Мне важно чувствовать защищенность и уверенность в завтрашнем дне.", "category": "SECURITY"},
    {"text": "Я предпочитаю эволюционные изменения революционным.", "category": "SECURITY"}
]

# ==================== ТЕСТ ПРОГРАММИРОВАНИЯ (20 вопросов) ====================
PROGRAMMING_QUESTIONS = [
    {"text": "Что выведет следующий код Python: print(type([]))?", "options": ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'dict'>"], "correct": 0},
    {"text": "Какой из этих типов данных является неизменяемым в Python?", "options": ["Список", "Словарь", "Кортеж", "Множество"], "correct": 2},
    {"text": "Что означает SQL?", "options": ["Structured Query Language", "Simple Question Language", "Standard Query Logic", "System Query Language"], "correct": 0},
    {"text": "Какой метод HTTP используется для получения данных?", "options": ["POST", "GET", "PUT", "DELETE"], "correct": 1},
    {"text": "Что такое 'this' в JavaScript?", "options": ["Ссылка на текущий объект", "Глобальная переменная", "Ключевое слово для создания объектов", "Функция-конструктор"], "correct": 0},
    {"text": "Как объявить переменную в CSS?", "options": ["--variable: value;", "var: value;", "$variable = value;", "variable: value;"], "correct": 0},
    {"text": "Что такое REST API?", "options": ["Архитектурный стиль для веб-сервисов", "Язык программирования", "База данных", "Фреймворк для Python"], "correct": 0},
    {"text": "Какой из этих алгоритмов имеет сложность O(log n)?", "options": ["Линейный поиск", "Бинарный поиск", "Пузырьковая сортировка", "Быстрая сортировка"], "correct": 1},
    {"text": "Что делает оператор '===' в JavaScript?", "options": ["Сравнение с приведением типов", "Строгое сравнение без приведения типов", "Присваивание значения", "Проверка на существование"], "correct": 1},
    {"text": "Какой протокол используется для безопасного соединения в вебе?", "options": ["HTTP", "FTP", "HTTPS", "SMTP"], "correct": 2},
    {"text": "Что такое API?", "options": ["Интерфейс программирования приложений", "База данных", "Язык программирования", "Операционная система"], "correct": 0},
    {"text": "Что означает HTML?", "options": ["Hyper Text Markup Language", "Home Tool Markup Language", "Hyperlinks and Text Markup", "High-Level Machine Language"], "correct": 0},
    {"text": "Какой язык НЕ для веба?", "options": ["JavaScript", "Python", "C++", "PHP"], "correct": 2},
    {"text": "Что такое CSS?", "options": ["Стили", "Скрипты", "Разметка", "База данных"], "correct": 0},
    {"text": "Как объявить переменную в JS?", "options": ["let x;", "var x;", "const x;", "Все варианты"], "correct": 3},
    {"text": "Что выведет: console.log(2 + '2')?", "options": ["4", "22", "Ошибка", "undefined"], "correct": 1},
    {"text": "Что такое React?", "options": ["Библиотека", "Фреймворк", "Язык", "База данных"], "correct": 0},
    {"text": "Что означает CRUD?", "options": ["Create Read Update Delete", "Code Run Update Debug", "Create Run Update Data", "Coding Rules"], "correct": 0},
    {"text": "Какой язык на сервере?", "options": ["Node.js", "Python", "PHP", "Все варианты"], "correct": 3},
    {"text": "База данных — это...", "options": ["Хранилище данных", "Таблица", "Сервер", "Файл"], "correct": 0}
]

# ==================== КНОПКИ МЕНЮ ====================
def get_main_menu():
    keyboard = [
        ["📘 Тест Томаса-Килманна"],
        ["🧠 Тест Кейрси"],
        ["🔥 Мотивационный тест"],
        ["💻 Тест программирования"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== ОБРАБОТЧИКИ ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот с психологическими и профессиональными тестами.\n\nВыбери тест из меню 👇",
        reply_markup=get_main_menu()
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "📘 Тест Томаса-Килманна":
        user_data[user_id] = {"test": "thomas", "question": 0, "answers": [], "total": len(THOMAS_QUESTIONS)}
        await send_question(update, user_id, THOMAS_QUESTIONS)
    elif text == "🧠 Тест Кейрси":
        user_data[user_id] = {"test": "keirsey", "question": 0, "answers": [], "total": len(KEIRSEY_QUESTIONS)}
        await send_question(update, user_id, KEIRSEY_QUESTIONS)
    elif text == "🔥 Мотивационный тест":
        user_data[user_id] = {"test": "motivation", "question": 0, "answers": [], "total": len(MOTIVATION_QUESTIONS)}
        await send_motivation_question(update, user_id)
    elif text == "💻 Тест программирования":
        user_data[user_id] = {"test": "programming", "question": 0, "answers": [], "total": len(PROGRAMMING_QUESTIONS)}
        await send_programming_question(update, user_id)

async def send_question(update, user_id, questions):
    data = user_data[user_id]
    q = questions[data["question"]]
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{i}")] for i, opt in enumerate(q["options"])]
    await update.message.reply_text(
        f"📋 *Вопрос {data['question']+1} из {data['total']}*\n\n{q['text']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def send_motivation_question(update, user_id):
    data = user_data[user_id]
    q = MOTIVATION_QUESTIONS[data["question"]]
    keyboard = [[InlineKeyboardButton(str(i), callback_data=f"scale_{i}") for i in range(1, 6)]]
    await update.message.reply_text(
        f"📋 *Вопрос {data['question']+1} из {data['total']}*\n\n{q['text']}\n\nОцените от 1 до 5:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def send_programming_question(update, user_id):
    data = user_data[user_id]
    q = PROGRAMMING_QUESTIONS[data["question"]]
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"prog_{i}")] for i, opt in enumerate(q["options"])]
    await update.message.reply_text(
        f"💻 *Вопрос {data['question']+1} из {data['total']}*\n\n{q['text']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = user_data.get(user_id)
    
    if not data:
        await query.edit_message_text("Начните тест заново командой /start")
        return
    
    if query.data.startswith("ans_"):
        answer_idx = int(query.data.split("_")[1])
        data["answers"].append(answer_idx)
        data["question"] += 1
        
        questions = THOMAS_QUESTIONS if data["test"] == "thomas" else KEIRSEY_QUESTIONS
        if data["question"] >= data["total"]:
            await finish_ab_test(query, user_id)
        else:
            q = questions[data["question"]]
            keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{i}")] for i, opt in enumerate(q["options"])]
            await query.edit_message_text(
                f"📋 *Вопрос {data['question']+1} из {data['total']}*\n\n{q['text']}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
    
    elif query.data.startswith("scale_"):
        score = int(query.data.split("_")[1])
        data["answers"].append(score)
        data["question"] += 1
        
        if data["question"] >= data["total"]:
            await finish_motivation_test(query, user_id)
        else:
            q = MOTIVATION_QUESTIONS[data["question"]]
            keyboard = [[InlineKeyboardButton(str(i), callback_data=f"scale_{i}") for i in range(1, 6)]]
            await query.edit_message_text(
                f"📋 *Вопрос {data['question']+1} из {data['total']}*\n\n{q['text']}\n\nОцените от 1 до 5:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
    
    elif query.data.startswith("prog_"):
        answer_idx = int(query.data.split("_")[1])
        data["answers"].append(answer_idx)
        data["question"] += 1
        
        if data["question"] >= data["total"]:
            await finish_programming_test(query, user_id)
        else:
            q = PROGRAMMING_QUESTIONS[data["question"]]
            keyboard = [[InlineKeyboardButton(opt, callback_data=f"prog_{i}")] for i, opt in enumerate(q["options"])]
            await query.edit_message_text(
                f"💻 *Вопрос {data['question']+1} из {data['total']}*\n\n{q['text']}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

async def finish_ab_test(query, user_id):
    data = user_data[user_id]
    questions = THOMAS_QUESTIONS if data["test"] == "thomas" else KEIRSEY_QUESTIONS
    scores = {"COMPETING":0, "COLLABORATING":0, "COMPROMISING":0, "AVOIDING":0, "ACCOMMODATING":0}
    
    for i, ans in enumerate(data["answers"]):
        strategy = questions[i]["scores"][ans]
        if strategy in scores:
            scores[strategy] += 1
    
    main = max(scores, key=scores.get)
    names = {"COMPETING":"Соперничество", "COLLABORATING":"Сотрудничество", 
             "COMPROMISING":"Компромисс", "AVOIDING":"Избегание", "ACCOMMODATING":"Приспособление"}
    
    result = f"🏆 *Результат теста Томаса-Килманна*\n\n" if data["test"] == "thomas" else f"🧠 *Результат теста Кейрси*\n\n"
    result += f"Ваша основная стратегия: *{names[main]}* ({scores[main]} баллов)\n\n"
    result += f"📊 Распределение:\n" + "\n".join([f"• {names[k]}: {v}" for k, v in scores.items()])
    
    await query.edit_message_text(result, parse_mode="Markdown")
    await query.message.reply_text("✅ Тест завершен! Выберите другой тест 👇", reply_markup=get_main_menu())
    del user_data[user_id]

async def finish_motivation_test(query, user_id):
    data = user_data[user_id]
    scores = {"ACHIEVEMENT":0, "POWER":0, "AFFILIATION":0, "RECOGNITION":0, "SECURITY":0}
    counts = {k:0 for k in scores}
    
    for i, ans in enumerate(data["answers"]):
        cat = MOTIVATION_QUESTIONS[i]["category"]
        scores[cat] += ans
        counts[cat] += 1
    
    avg = {cat: round(scores[cat]/counts[cat], 1) for cat in scores if counts[cat] > 0}
    main = max(avg, key=avg.get)
    names = {"ACHIEVEMENT":"Достижение", "POWER":"Власть", "AFFILIATION":"Причастность", 
             "RECOGNITION":"Признание", "SECURITY":"Безопасность"}
    
    result = f"🔥 *Результат мотивационного теста*\n\n"
    result += f"Ваш ведущий мотив: *{names[main]}* ({avg[main]}/5)\n\n"
    result += f"📊 Все мотивы:\n" + "\n".join([f"• {names[k]}: {v}/5" for k, v in avg.items()])
    
    await query.edit_message_text(result, parse_mode="Markdown")
    await query.message.reply_text("✅ Тест завершен! Выберите другой тест 👇", reply_markup=get_main_menu())
    del user_data[user_id]

async def finish_programming_test(query, user_id):
    data = user_data[user_id]
    correct = sum(1 for i, ans in enumerate(data["answers"]) if ans == PROGRAMMING_QUESTIONS[i]["correct"])
    total = len(PROGRAMMING_QUESTIONS)
    percent = round(correct / total * 100)
    
    if percent >= 80:
        level = "🏆 Эксперт! Отличные знания!"
    elif percent >= 60:
        level = "📚 Хороший уровень, продолжайте!"
    elif percent >= 40:
        level = "🌱 Начинающий, есть куда расти"
    else:
        level = "📖 Стоит подтянуть основы"
    
    result = f"💻 *Результат теста программирования*\n\n"
    result += f"Правильных ответов: *{correct} из {total}* ({percent}%)\n\n{level}"
    
    await query.edit_message_text(result, parse_mode="Markdown")
    await query.message.reply_text("✅ Тест завершен! Выберите другой тест 👇", reply_markup=get_main_menu())
    del user_data[user_id]

# ==================== ЗАПУСК ====================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
