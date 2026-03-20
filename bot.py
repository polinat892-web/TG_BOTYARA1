import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ==================== НАСТРОЙКИ ====================
# ВСТАВЬТЕ ВАШ ТОКЕН СЮДА (от @BotFather)
TOKEN = "ВАШ_ТОКЕН_СЮДА"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==================== ХРАНИЛИЩЕ СОСТОЯНИЙ ====================
user_data = {}

# ==================== ТЕСТ ТОМАСА-КИЛМАННА (30 вопросов) ====================
THOMAS_QUESTIONS = [
    {"id": 1, "text": "Когда возникает конфликт, я обычно...", "options": ["Настаиваю на своем решении, чтобы добиться желаемого", "Стараюсь найти решение, которое устроит всех"], "scores": ["COMPETING", "COLLABORATING"]},
    {"id": 2, "text": "Если коллега не согласен с моим предложением, я...", "options": ["Предлагаю найти золотую середину", "Предлагаю отложить обсуждение на потом"], "scores": ["COMPROMISING", "AVOIDING"]},
    {"id": 3, "text": "Когда конфликт затрагивает важные для меня вопросы, я...", "options": ["Борюсь за свои интересы до конца", "Иду на уступки, чтобы сохранить отношения"], "scores": ["COMPETING", "ACCOMMODATING"]},
    {"id": 4, "text": "В споре с близким человеком я обычно...", "options": ["Стараюсь понять его точку зрения и найти общее решение", "Предлагаю обоим немного уступить"], "scores": ["COLLABORATING", "COMPROMISING"]},
    {"id": 5, "text": "Если начальник дает невыполнимое задание, я...", "options": ["Молча выполняю, как могу", "Избегаю обсуждения этого вопроса"], "scores": ["ACCOMMODATING", "AVOIDING"]},
    {"id": 6, "text": "Когда в команде возникают разногласия, я...", "options": ["Предлагаю обсудить все мнения и прийти к консенсусу", "Настаиваю на своем варианте как наиболее правильном"], "scores": ["COLLABORATING", "COMPETING"]},
    {"id": 7, "text": "Если партнер по проекту не выполняет свою часть работы, я...", "options": ["Говорю, что сделаю его часть, чтобы проект не пострадал", "Предлагаю разделить работу по-другому"], "scores": ["ACCOMMODATING", "COMPROMISING"]},
    {"id": 8, "text": "Когда спор становится слишком эмоциональным, я...", "options": ["Предлагаю сделать перерыв и вернуться к обсуждению позже", "Стараюсь успокоить всех и найти компромисс"], "scores": ["AVOIDING", "COMPROMISING"]},
    {"id": 9, "text": "Если мое мнение не учитывают при принятии решения, я...", "options": ["Настойчиво требую, чтобы мое мнение было услышано", "Стараюсь доказать свою правоту с помощью фактов и логики"], "scores": ["COMPETING", "COLLABORATING"]},
    {"id": 10, "text": "Когда конфликт не принципиален для меня, я...", "options": ["Легко соглашаюсь с другим человеком", "Избегаю дальнейшего обсуждения"], "scores": ["ACCOMMODATING", "AVOIDING"]},
    {"id": 11, "text": "В конфликте с подчиненным я...", "options": ["Требую выполнения моих указаний без возражений", "Стараюсь объяснить свою позицию и выслушать его"], "scores": ["COMPETING", "COLLABORATING"]},
    {"id": 12, "text": "Если друзья спорят, я...", "options": ["Предлагаю каждому немного уступить", "Стараюсь их помирить, найдя общее решение"], "scores": ["COMPROMISING", "COLLABORATING"]},
    {"id": 13, "text": "Когда меня критикуют незаслуженно, я...", "options": ["Молча принимаю критику, чтобы не усугублять ситуацию", "Избегаю дальнейшего общения с этим человеком"], "scores": ["ACCOMMODATING", "AVOIDING"]},
    {"id": 14, "text": "В переговорах я обычно...", "options": ["Стараюсь добиться максимальной выгоды для себя", "Ищу вариант, где обе стороны получат что-то важное"], "scores": ["COMPETING", "COLLABORATING"]},
    {"id": 15, "text": "Если коллега постоянно перебивает меня на совещаниях, я...", "options": ["Терпеливо жду, когда он закончит", "Предлагаю установить правила выступления"], "scores": ["ACCOMMODATING", "COMPROMISING"]},
    {"id": 16, "text": "Когда проект находится под угрозой из-за разногласий в команде, я...", "options": ["Беру руководство на себя и принимаю решение единолично", "Организую мозговой штурм для поиска лучшего решения"], "scores": ["COMPETING", "COLLABORATING"]},
    {"id": 17, "text": "Если супруг(а) хочет провести отпуск не там, где хочу я, я...", "options": ["Предлагаю разделить отпуск или выбрать нейтральное место", "Соглашаюсь с его(ее) выбором, чтобы избежать ссоры"], "scores": ["COMPROMISING", "ACCOMMODATING"]},
    {"id": 18, "text": "Когда начальник неправ, но настаивает на своем, я...", "options": ["Молча выполняю указания, даже если не согласен", "Стараюсь мягко предложить альтернативу"], "scores": ["ACCOMMODATING", "COLLABORATING"]},
    {"id": 19, "text": "В конфликте из-за ресурсов на работе я...", "options": ["Требую свою долю, аргументируя потребностями", "Предлагаю поделить ресурсы поровну"], "scores": ["COMPETING", "COMPROMISING"]},
    {"id": 20, "text": "Если меня обвиняют в чем-то, чего я не делал, я...", "options": ["Резко отвергаю обвинения и защищаюсь", "Спокойно предлагаю разобраться в ситуации вместе"], "scores": ["COMPETING", "COLLABORATING"]},
    {"id": 21, "text": "Когда сроки горят, а команда не может договориться, я...", "options": ["Принимаю решение сам и требую выполнения", "Предлагаю временное решение, чтобы успеть в срок"], "scores": ["COMPETING", "COMPROMISING"]},
    {"id": 22, "text": "Если друг постоянно опаздывает на встречи, я...", "options": ["Молча терплю, чтобы не портить отношения", "Перестаю назначать встречи заранее"], "scores": ["ACCOMMODATING", "AVOIDING"]},
    {"id": 23, "text": "В споре о политике или религии я...", "options": ["Избегаю таких тем в разговоре", "Стараюсь найти точки соприкосновения"], "scores": ["AVOIDING", "COLLABORATING"]},
    {"id": 24, "text": "Когда клиент недоволен, но его требования нереалистичны, я...", "options": ["Предлагаю частичное удовлетворение требований", "Объясняю, почему требования невыполнимы, и ищу альтернативу"], "scores": ["COMPROMISING", "COLLABORATING"]},
    {"id": 25, "text": "Если коллега присваивает себе мои идеи, я...", "options": ["Прямо заявляю о своем авторстве при всех", "Говорю с ним наедине о ситуации"], "scores": ["COMPETING", "COLLABORATING"]},
    {"id": 26, "text": "Когда в семье спорят о распределении обязанностей, я...", "options": ["Предлагаю составить график дежурств", "Беру на себя больше, чтобы избежать конфликтов"], "scores": ["COMPROMISING", "ACCOMMODATING"]},
    {"id": 27, "text": "Если проектная группа не может выбрать технологию, я...", "options": ["Предлагаю протестировать несколько вариантов", "Настаиваю на той технологии, в которой лучше разбираюсь"], "scores": ["COLLABORATING", "COMPETING"]},
    {"id": 28, "text": "Когда меня перебивают в важном разговоре, я...", "options": ["Терпеливо жду своей очереди", "Вежливо, но твердо продолжаю говорить"], "scores": ["ACCOMMODATING", "COMPETING"]},
    {"id": 29, "text": "Если команда не может согласовать дизайн проекта, я...", "options": ["Предлагаю проголосовать за лучший вариант", "Объединяю элементы из разных предложений"], "scores": ["COMPROMISING", "COLLABORATING"]},
    {"id": 30, "text": "Когда конфликт угрожает дедлайну, я...", "options": ["Предлагаю быстро принять компромиссное решение", "Настаиваю на правильном решении, даже если это займет время"], "scores": ["COMPROMISING", "COMPETING"]}
]

# ==================== ТЕСТ КЕЙРСИ (70 вопросов) ====================
KEIRSEY_QUESTIONS = [
    {"id": 1, "text": "В компании я обычно:", "options": ["Наблюдаю и слушаю", "Активно общаюсь"], "scores": ["SP", "NF"]},
    {"id": 2, "text": "При принятии решений я больше полагаюсь на:", "options": ["Логику и факты", "Чувства и эмоции"], "scores": ["NT", "NF"]},
    {"id": 3, "text": "Я предпочитаю:", "options": ["Планировать заранее", "Действовать спонтанно"], "scores": ["SJ", "SP"]},
    {"id": 4, "text": "Для меня важнее:", "options": ["Сохранение традиций", "Инновации и изменения"], "scores": ["SJ", "NT"]},
    {"id": 5, "text": "В работе я ценю:", "options": ["Стабильность и порядок", "Свободу и гибкость"], "scores": ["SJ", "SP"]},
    {"id": 6, "text": "Я скорее:", "options": ["Реалист и практик", "Мечтатель и идеалист"], "scores": ["SP", "NF"]},
    {"id": 7, "text": "В общении я:", "options": ["Прямолинеен и честен", "Тактичен и дипломатичен"], "scores": ["NT", "NF"]},
    {"id": 8, "text": "Мне нравится:", "options": ["Следовать правилам", "Находить обходные пути"], "scores": ["SJ", "SP"]},
    {"id": 9, "text": "Я больше интересуюсь:", "options": ["Конкретными фактами", "Теориями и идеями"], "scores": ["SJ", "NT"]},
    {"id": 10, "text": "В сложной ситуации я:", "options": ["Сохраняю спокойствие", "Проявляю эмоции"], "scores": ["NT", "NF"]},
    {"id": 11, "text": "Я предпочитаю:", "options": ["Известное и проверенное", "Новое и неизведанное"], "scores": ["SJ", "NT"]},
    {"id": 12, "text": "Для меня важнее:", "options": ["Справедливость", "Гармония"], "scores": ["NT", "NF"]},
    {"id": 13, "text": "Я скорее:", "options": ["Осторожный и осмотрительный", "Рисковый и смелый"], "scores": ["SJ", "SP"]},
    {"id": 14, "text": "В обучении я предпочитаю:", "options": ["Практический опыт", "Теоретические знания"], "scores": ["SP", "NT"]},
    {"id": 15, "text": "Я ценю в людях:", "options": ["Надежность и ответственность", "Креативность и воображение"], "scores": ["SJ", "NF"]},
    {"id": 16, "text": "Мой подход к жизни:", "options": ["Серьезный и ответственный", "Легкий и спонтанный"], "scores": ["SJ", "SP"]},
    {"id": 17, "text": "Я больше ориентирован на:", "options": ["Настоящее", "Будущее"], "scores": ["SP", "NT"]},
    {"id": 18, "text": "В конфликте я стремлюсь:", "options": ["Установить истину", "Сохранить отношения"], "scores": ["NT", "NF"]},
    {"id": 19, "text": "Я предпочитаю работу:", "options": ["Структурированную и четкую", "Свободную и творческую"], "scores": ["SJ", "NF"]},
    {"id": 20, "text": "Мне важнее:", "options": ["Эффективность", "Эстетика"], "scores": ["NT", "NF"]},
    {"id": 21, "text": "Я скорее:", "options": ["Традиционалист", "Новатор"], "scores": ["SJ", "NT"]},
    {"id": 22, "text": "В свободное время я предпочитаю:", "options": ["Активный отдых", "Спокойные занятия"], "scores": ["SP", "SJ"]},
    {"id": 23, "text": "Я больше доверяю:", "options": ["Опыту", "Интуиции"], "scores": ["SJ", "NF"]},
    {"id": 24, "text": "При принятии решений я:", "options": ["Взвешиваю все за и против", "Доверяю внутреннему голосу"], "scores": ["NT", "NF"]},
    {"id": 25, "text": "Я ценю в себе:", "options": ["Практичность", "Творчество"], "scores": ["SP", "NF"]},
    {"id": 26, "text": "Мне комфортнее:", "options": ["В одиночестве", "В компании"], "scores": ["NT", "NF"]},
    {"id": 27, "text": "Я предпочитаю:", "options": ["Конкретные инструкции", "Общие указания"], "scores": ["SJ", "NT"]},
    {"id": 28, "text": "Для меня важнее:", "options": ["Факты", "Возможности"], "scores": ["SJ", "NT"]},
    {"id": 29, "text": "Я скорее:", "options": ["Реалист", "Идеалист"], "scores": ["SP", "NF"]},
    {"id": 30, "text": "В отношениях я ценю:", "options": ["Стабильность", "Страсть"], "scores": ["SJ", "SP"]},
    {"id": 31, "text": "Я предпочитаю:", "options": ["Избегать конфликтов", "Решать проблемы открыто"], "scores": ["NF", "NT"]},
    {"id": 32, "text": "Мне важнее:", "options": ["Быть полезным", "Быть уникальным"], "scores": ["SJ", "NF"]},
    {"id": 33, "text": "Я скорее:", "options": ["Терпеливый", "Нетерпеливый"], "scores": ["SJ", "SP"]},
    {"id": 34, "text": "В работе я предпочитаю:", "options": ["Закончить одно дело", "Работать над несколькими"], "scores": ["SJ", "SP"]},
    {"id": 35, "text": "Я больше ориентирован на:", "options": ["Процесс", "Результат"], "scores": ["SP", "NT"]},
    {"id": 36, "text": "Мне нравится:", "options": ["Следовать плану", "Импровизировать"], "scores": ["SJ", "SP"]},
    {"id": 37, "text": "Я ценю в информации:", "options": ["Точность", "Интересность"], "scores": ["NT", "NF"]},
    {"id": 38, "text": "Я скорее:", "options": ["Консервативный", "Либеральный"], "scores": ["SJ", "NT"]},
    {"id": 39, "text": "Для меня важнее:", "options": ["Быть правым", "Быть понятым"], "scores": ["NT", "NF"]},
    {"id": 40, "text": "Я предпочитаю:", "options": ["Рутинную работу", "Разнообразные задачи"], "scores": ["SJ", "SP"]},
    {"id": 41, "text": "Мне комфортнее:", "options": ["В знакомой обстановке", "В новых ситуациях"], "scores": ["SJ", "SP"]},
    {"id": 42, "text": "Я больше доверяю:", "options": ["Статистике", "Личному опыту"], "scores": ["NT", "NF"]},
    {"id": 43, "text": "Я скорее:", "options": ["Организованный", "Гибкий"], "scores": ["SJ", "SP"]},
    {"id": 44, "text": "Для меня важнее:", "options": ["Здравый смысл", "Воображение"], "scores": ["SP", "NF"]},
    {"id": 45, "text": "Я предпочитаю:", "options": ["Прямые ответы", "Дипломатичные ответы"], "scores": ["NT", "NF"]},
    {"id": 46, "text": "Мне важнее:", "options": ["Содержание", "Форма"], "scores": ["NT", "NF"]},
    {"id": 47, "text": "Я скорее:", "options": ["Последовательный", "Спонтанный"], "scores": ["SJ", "SP"]},
    {"id": 48, "text": "В обучении я предпочитаю:", "options": ["Структурированные курсы", "Самостоятельное изучение"], "scores": ["SJ", "NT"]},
    {"id": 49, "text": "Я ценю в работе:", "options": ["Стабильность", "Возможности для роста"], "scores": ["SJ", "NT"]},
    {"id": 50, "text": "Мой стиль общения:", "options": ["Формальный", "Неформальный"], "scores": ["SJ", "SP"]},
    {"id": 51, "text": "Я скорее:", "options": ["Осторожный в высказываниях", "Откровенный"], "scores": ["NF", "NT"]},
    {"id": 52, "text": "Для меня важнее:", "options": ["Фактическая правда", "Эмоциональная правда"], "scores": ["NT", "NF"]},
    {"id": 53, "text": "Я предпочитаю:", "options": ["Избегать ошибок", "Экспериментировать"], "scores": ["SJ", "SP"]},
    {"id": 54, "text": "Мне комфортнее:", "options": ["С четкими инструкциями", "С свободой действий"], "scores": ["SJ", "NT"]},
    {"id": 55, "text": "Я скорее:", "options": ["Реалистичный в целях", "Амбициозный"], "scores": ["SP", "NT"]},
    {"id": 56, "text": "Для меня важнее:", "options": ["Процедуры", "Результаты"], "scores": ["SJ", "NT"]},
    {"id": 57, "text": "Я предпочитаю:", "options": ["Работать в одиночку", "Работать в команде"], "scores": ["NT", "NF"]},
    {"id": 58, "text": "Мне важнее:", "options": ["Быть компетентным", "Быть любимым"], "scores": ["NT", "NF"]},
    {"id": 59, "text": "Я скорее:", "options": ["Прагматик", "Мечтатель"], "scores": ["SP", "NF"]},
    {"id": 60, "text": "В принятии решений я:", "options": ["Медленный и обдуманный", "Быстрый и решительный"], "scores": ["SJ", "SP"]},
    {"id": 61, "text": "Я ценю в себе:", "options": ["Надежность", "Оригинальность"], "scores": ["SJ", "NF"]},
    {"id": 62, "text": "Мне важнее:", "options": ["Соответствовать стандартам", "Выделяться из толпы"], "scores": ["SJ", "NF"]},
    {"id": 63, "text": "Я скорее:", "options": ["Осторожный с деньгами", "Щедрый"], "scores": ["SJ", "NF"]},
    {"id": 64, "text": "Я предпочитаю:", "options": ["Известные маршруты", "Новые пути"], "scores": ["SJ", "SP"]},
    {"id": 65, "text": "Мне комфортнее:", "options": ["В структурированной среде", "В хаотичной среде"], "scores": ["SJ", "SP"]},
    {"id": 66, "text": "Я скорее:", "options": ["Последовательный в привычках", "Разнообразный в интересах"], "scores": ["SJ", "SP"]},
    {"id": 67, "text": "Для меня важнее:", "options": ["Закончить начатое", "Начать новое"], "scores": ["SJ", "SP"]},
    {"id": 68, "text": "Я предпочитаю:", "options": ["Детальные описания", "Общие концепции"], "scores": ["SJ", "NT"]},
    {"id": 69, "text": "Мне важнее:", "options": ["Практическая польза", "Теоретическая ценность"], "scores": ["SP", "NT"]},
    {"id": 70, "text": "Я скорее:", "options": ["Терпимый к рутине", "Ищущий новизны"], "scores": ["SJ", "SP"]}
]

# ==================== МОТИВАЦИОННЫЙ ТЕСТ (50 вопросов) ====================
MOTIVATION_QUESTIONS = [
    {"id": 1, "text": "Мне важно постоянно совершенствовать свои навыки и умения.", "category": "ACHIEVEMENT"},
    {"id": 2, "text": "Я ставлю перед собой амбициозные цели и стремлюсь их достичь.", "category": "ACHIEVEMENT"},
    {"id": 3, "text": "Мне нравится браться за сложные задачи, которые требуют максимум усилий.", "category": "ACHIEVEMENT"},
    {"id": 4, "text": "Я получаю удовольствие от решения трудных проблем.", "category": "ACHIEVEMENT"},
    {"id": 5, "text": "Для меня важно быть лучшим в том, чем я занимаюсь.", "category": "ACHIEVEMENT"},
    {"id": 6, "text": "Я стремлюсь к профессиональному росту и развитию.", "category": "ACHIEVEMENT"},
    {"id": 7, "text": "Мне важно видеть конкретные результаты своей работы.", "category": "ACHIEVEMENT"},
    {"id": 8, "text": "Я часто сравниваю свои достижения с достижениями других.", "category": "ACHIEVEMENT"},
    {"id": 9, "text": "Невыполненная задача вызывает у меня дискомфорт.", "category": "ACHIEVEMENT"},
    {"id": 10, "text": "Я готов много работать ради достижения успеха.", "category": "ACHIEVEMENT"},
    {"id": 11, "text": "Мне нравится брать на себя ответственность за других людей.", "category": "POWER"},
    {"id": 12, "text": "Я чувствую себя комфортно, когда руковожу проектом или командой.", "category": "POWER"},
    {"id": 13, "text": "Мне важно иметь возможность влиять на решения других.", "category": "POWER"},
    {"id": 14, "text": "Я получаю удовольствие от того, что могу контролировать ситуацию.", "category": "POWER"},
    {"id": 15, "text": "Мне нравится убеждать других в своей точке зрения.", "category": "POWER"},
    {"id": 16, "text": "Я стремлюсь к положению, которое дает власть и авторитет.", "category": "POWER"},
    {"id": 17, "text": "Мне важно, чтобы мои указания выполнялись без возражений.", "category": "POWER"},
    {"id": 18, "text": "Я чувствую себя увереннее, когда руковожу процессом.", "category": "POWER"},
    {"id": 19, "text": "Мне нравится организовывать работу других людей.", "category": "POWER"},
    {"id": 20, "text": "Я стремлюсь к позиции, где можно принимать важные решения.", "category": "POWER"},
    {"id": 21, "text": "Для меня важно иметь хорошие отношения с коллегами.", "category": "AFFILIATION"},
    {"id": 22, "text": "Я ценю теплую и дружескую атмосферу на работе.", "category": "AFFILIATION"},
    {"id": 23, "text": "Мне нравится работать в команде, а не в одиночку.", "category": "AFFILIATION"},
    {"id": 24, "text": "Я стремлюсь быть частью коллектива, чувствовать принадлежность.", "category": "AFFILIATION"},
    {"id": 25, "text": "Для меня важно поддерживать контакты с людьми вне работы.", "category": "AFFILIATION"},
    {"id": 26, "text": "Я избегаю конфликтов и стремлюсь к гармонии в отношениях.", "category": "AFFILIATION"},
    {"id": 27, "text": "Мне нравится помогать другим и чувствовать себя полезным.", "category": "AFFILIATION"},
    {"id": 28, "text": "Я ценю сотрудничество больше, чем конкуренцию.", "category": "AFFILIATION"},
    {"id": 29, "text": "Одиночество на работе вызывает у меня дискомфорт.", "category": "AFFILIATION"},
    {"id": 30, "text": "Мне важно чувствовать себя принятым в коллективе.", "category": "AFFILIATION"},
    {"id": 31, "text": "Мне важно, чтобы другие ценили мои заслуги.", "category": "RECOGNITION"},
    {"id": 32, "text": "Я хочу, чтобы мои успехи были заметны окружающим.", "category": "RECOGNITION"},
    {"id": 33, "text": "Похвала и благодарность мотивируют меня работать лучше.", "category": "RECOGNITION"},
    {"id": 34, "text": "Мне нравится, когда меня публично отмечают за хорошую работу.", "category": "RECOGNITION"},
    {"id": 35, "text": "Я стремлюсь к позициям, которые приносят уважение и почет.", "category": "RECOGNITION"},
    {"id": 36, "text": "Для меня важно иметь статус и репутацию в профессиональной среде.", "category": "RECOGNITION"},
    {"id": 37, "text": "Мне приятно, когда другие обращаются ко мне за советом.", "category": "RECOGNITION"},
    {"id": 38, "text": "Я ценю официальные награды и знаки отличия.", "category": "RECOGNITION"},
    {"id": 39, "text": "Мне важно, чтобы мой вклад в общее дело был замечен.", "category": "RECOGNITION"},
    {"id": 40, "text": "Я стремлюсь к тому, чтобы мое имя было известно в профессиональных кругах.", "category": "RECOGNITION"},
    {"id": 41, "text": "Для меня важна стабильность и предсказуемость на работе.", "category": "SECURITY"},
    {"id": 42, "text": "Я предпочитаю ясные инструкции и четкие правила.", "category": "SECURITY"},
    {"id": 43, "text": "Мне важно иметь гарантированную работу и стабильный доход.", "category": "SECURITY"},
    {"id": 44, "text": "Я избегаю ситуаций с неопределенностью и риском.", "category": "SECURITY"},
    {"id": 45, "text": "Для меня важны социальные гарантии и пенсионное обеспечение.", "category": "SECURITY"},
    {"id": 46, "text": "Я предпочитаю работать в надежной и проверенной компании.", "category": "SECURITY"},
    {"id": 47, "text": "Мне комфортнее в структурированной и организованной среде.", "category": "SECURITY"},
    {"id": 48, "text": "Я ценю долгосрочные контракты и постоянную занятость.", "category": "SECURITY"},
    {"id": 49, "text": "Мне важно чувствовать защищенность и уверенность в завтрашнем дне.", "category": "SECURITY"},
    {"id": 50, "text": "Я предпочитаю эволюционные изменения революционным.", "category": "SECURITY"}
]

# ==================== ТЕСТ ПРОГРАММИРОВАНИЯ (20 вопросов) ====================
PROGRAMMING_QUESTIONS = [
    {"id": 1, "text": "Что выведет следующий код Python: print(type([]))?", "options": ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'dict'>"], "correct": 0},
    {"id": 2, "text": "Какой из этих типов данных является неизменяемым в Python?", "options": ["Список", "Словарь", "Кортеж", "Множество"], "correct": 2},
    {"id": 3, "text": "Что означает SQL?", "options": ["Structured Query Language", "Simple Question Language", "Standard Query Logic", "System Query Language"], "correct": 0},
    {"id": 4, "text": "Какой метод HTTP используется для получения данных?", "options": ["POST", "GET", "PUT", "DELETE"], "correct": 1},
    {"id": 5, "text": "Что такое 'this' в JavaScript?", "options": ["Ссылка на текущий объект", "Глобальная переменная", "Ключевое слово для создания объектов", "Функция-конструктор"], "correct": 0},
    {"id": 6, "text": "Как объявить переменную в CSS?", "options": ["--variable: value;", "var: value;", "$variable = value;", "variable: value;"], "correct": 0},
    {"id": 7, "text": "Что такое REST API?", "options": ["Архитектурный стиль для веб-сервисов", "Язык программирования", "База данных", "Фреймворк для Python"], "correct": 0},
    {"id": 8, "text": "Какой из этих алгоритмов имеет сложность O(log n)?", "options": ["Линейный поиск", "Бинарный поиск", "Пузырьковая сортировка", "Быстрая сортировка"], "correct": 1},
    {"id": 9, "text": "Что делает оператор '===' в JavaScript?", "options": ["Сравнение с приведением типов", "Строгое сравнение без приведения типов", "Присваивание значения", "Проверка на существование"], "correct": 1},
    {"id": 10, "text": "Какой протокол используется для безопасного соединения в вебе?", "options": ["HTTP", "FTP", "HTTPS", "SMTP"], "correct": 2},
    {"id": 11, "text": "Что такое API?", "options": ["Интерфейс программирования приложений", "База данных", "Язык программирования", "Операционная система"], "correct": 0},
    {"id": 12, "text": "Что означает HTML?", "options": ["Hyper Text Markup Language", "Home Tool Markup Language", "Hyperlinks and Text Markup", "High-Level Machine Language"], "correct": 0},
    {"id": 13, "text": "Какой язык НЕ для веба?", "options": ["JavaScript", "Python", "C++", "PHP"], "correct": 2},
    {"id": 14, "text": "Что такое CSS?", "options": ["Стили", "Скрипты", "Разметка", "База данных"], "correct": 0},
    {"id": 15, "text": "Как объявить переменную в JS?", "options": ["let x;", "var x;", "const x;", "Все варианты"], "correct": 3},
    {"id": 16, "text": "Что выведет: console.log(2 + '2')?", "options": ["4", "22", "Ошибка", "undefined"], "correct": 1},
    {"id": 17, "text": "Что такое React?", "options": ["Библиотека", "Фреймворк", "Язык", "База данных"], "correct": 0},
    {"id": 18, "text": "Что означает CRUD?", "options": ["Create Read Update Delete", "Code Run Update Debug", "Create Run Update Data", "Coding Rules"], "correct": 0},
    {"id": 19, "text": "Какой язык на сервере?", "options": ["Node.js", "Python", "PHP", "Все варианты"], "correct": 3},
    {"id": 20, "text": "База данных — это...", "options": ["Хранилище данных", "Таблица", "Сервер", "Файл"], "correct": 0}
]

# ==================== КНОПКИ МЕНЮ ====================
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Тест Томаса-Килманна")],
            [KeyboardButton(text="🧠 Тест Кейрси")],
            [KeyboardButton(text="🔥 Мотивационный тест")],
            [KeyboardButton(text="💻 Тест программирования")]
        ],
        resize_keyboard=True
    )
    return keyboard

# ==================== ОБРАБОТЧИКИ ====================

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот с психологическими и профессиональными тестами.\n\n"
        "Выбери тест из меню ниже 👇",
        reply_markup=get_main_menu()
    )

@dp.message(lambda message: message.text == "📘 Тест Томаса-Килманна")
async def start_thomas(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        "test": "thomas",
        "question": 0,
        "answers": [],
        "total": len(THOMAS_QUESTIONS)
    }
    await send_question(message, user_id, THOMAS_QUESTIONS)

@dp.message(lambda message: message.text == "🧠 Тест Кейрси")
async def start_keirsey(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        "test": "keirsey",
        "question": 0,
        "answers": [],
        "total": len(KEIRSEY_QUESTIONS)
    }
    await send_question(message, user_id, KEIRSEY_QUESTIONS)

@dp.message(lambda message: message.text == "🔥 Мотивационный тест")
async def start_motivation(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        "test": "motivation",
        "question": 0,
        "answers": [],
        "total": len(MOTIVATION_QUESTIONS)
    }
    await send_motivation_question(message, user_id)

@dp.message(lambda message: message.text == "💻 Тест программирования")
async def start_programming(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        "test": "programming",
        "question": 0,
        "answers": [],
        "total": len(PROGRAMMING_QUESTIONS)
    }
    await send_programming_question(message, user_id)

async def send_question(message: types.Message, user_id, questions_list):
    data = user_data[user_id]
    q_index = data["question"]
    q = questions_list[q_index]
    
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(q["options"]):
        builder.add(InlineKeyboardButton(text=opt, callback_data=f"ans_{i}"))
    builder.adjust(1)
    
    await message.answer(
        f"📋 *Вопрос {q_index + 1} из {data['total']}*\n\n{q['text']}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

async def send_motivation_question(message: types.Message, user_id):
    data = user_data[user_id]
    q_index = data["question"]
    q = MOTIVATION_QUESTIONS[q_index]
    
    builder = InlineKeyboardBuilder()
    labels = ["1 ❌ Совсем не согласен", "2", "3 ⚖️ Нейтрально", "4", "5 ✅ Полностью согласен"]
    for i, label in enumerate(labels):
        builder.add(InlineKeyboardButton(text=label, callback_data=f"scale_{i+1}"))
    builder.adjust(5)
    
    await message.answer(
        f"📋 *Вопрос {q_index + 1} из {data['total']}*\n\n{q['text']}\n\n"
        f"Оцените от 1 до 5:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

async def send_programming_question(message: types.Message, user_id):
    data = user_data[user_id]
    q_index = data["question"]
    q = PROGRAMMING_QUESTIONS[q_index]
    
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(q["options"]):
        builder.add(InlineKeyboardButton(text=opt, callback_data=f"prog_{i}"))
    builder.adjust(1)
    
    await message.answer(
        f"💻 *Вопрос {q_index + 1} из {data['total']}*\n\n{q['text']}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data.startswith("ans_"))
async def handle_ab_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data or user_data[user_id]["test"] not in ["thomas", "keirsey"]:
        await callback.answer("Начните тест заново командой /start")
        return
    
    data = user_data[user_id]
    answer_idx = int(callback.data.split("_")[1])
    data["answers"].append(answer_idx)
    data["question"] += 1
    
    questions_list = THOMAS_QUESTIONS if data["test"] == "thomas" else KEIRSEY_QUESTIONS
    
    if data["question"] >= data["total"]:
        await finish_ab_test(callback.message, user_id)
    else:
        await send_question(callback.message, user_id, questions_list)
    
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("scale_"))
async def handle_motivation_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data or user_data[user_id]["test"] != "motivation":
        await callback.answer("Начните тест заново командой /start")
        return
    
    data = user_data[user_id]
    score = int(callback.data.split("_")[1])
    data["answers"].append(score)
    data["question"] += 1
    
    if data["question"] >= data["total"]:
        await finish_motivation_test(callback.message, user_id)
    else:
        await send_motivation_question(callback.message, user_id)
    
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("prog_"))
async def handle_programming_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data or user_data[user_id]["test"] != "programming":
        await callback.answer("Начните тест заново командой /start")
        return
    
    data = user_data[user_id]
    answer_idx = int(callback.data.split("_")[1])
    data["answers"].append(answer_idx)
    data["question"] += 1
    
    if data["question"] >= data["total"]:
        await finish_programming_test(callback.message, user_id)
    else:
        await send_programming_question(callback.message, user_id)
    
    await callback.answer()

async def finish_ab_test(message: types.Message, user_id):
    data = user_data[user_id]
    questions_list = THOMAS_QUESTIONS if data["test"] == "thomas" else KEIRSEY_QUESTIONS
    
    if data["test"] == "thomas":
        scores = {"COMPETING": 0, "COLLABORATING": 0, "COMPROMISING": 0, "AVOIDING": 0, "ACCOMMODATING": 0}
        for i, ans in enumerate(data["answers"]):
            strategy = questions_list[i]["scores"][ans]
            if strategy in scores:
                scores[strategy] += 1
        
        main = max(scores, key=scores.get)
        names = {"COMPETING": "Соперничество", "COLLABORATING": "Сотрудничество", 
                 "COMPROMISING": "Компромисс", "AVOIDING": "Избегание", "ACCOMMODATING": "Приспособление"}
        
        result = f"🏆 *Результат теста Томаса-Килманна*\n\n"
        result += f"Ваша основная стратегия: *{names[main]}* ({scores[main]} баллов)\n\n"
        result += f"📊 Распределение:\n"
        for k, v in scores.items():
            result += f"• {names[k]}: {v}\n"
    else:
        scores = {"SJ": 0, "NF": 0, "NT": 0, "SP": 0}
        for i, ans in enumerate(data["answers"]):
            type_key = questions_list[i]["scores"][ans]
            if type_key in scores:
                scores[type_key] += 1
        
        main = max(scores, key=scores.get)
        names = {"SJ": "Хранитель", "NF": "Идеалист", "NT": "Рационал", "SP": "Ремесленник"}
        descriptions = {
            "SJ": "Вы практичны, ответственны и цените традиции.",
            "NF": "Вы эмпатичны, творчески и стремитесь к гармонии.",
            "NT": "Вы логичны, инновационны и независимы.",
            "SP": "Вы спонтанны, адаптивны и живете настоящим."
        }
        
        result = f"🧠 *Результат теста Кейрси*\n\n"
        result += f"Ваш тип: *{names[main]} ({main})*\n\n"
        result += f"{descriptions[main]}\n\n"
        result += f"📊 Распределение:\n"
        for k, v in scores.items():
            result += f"• {names[k]}: {v}\n"
    
    await message.answer(result, parse_mode="Markdown")
    await message.answer(
        "✅ Тест завершен! Выберите другой тест из меню 👇",
        reply_markup=get_main_menu()
    )
    del user_data[user_id]

async def finish_motivation_test(message: types.Message, user_id):
    data = user_data[user_id]
    scores = {"ACHIEVEMENT": 0, "POWER": 0, "AFFILIATION": 0, "RECOGNITION": 0, "SECURITY": 0}
    counts = {"ACHIEVEMENT": 0, "POWER": 0, "AFFILIATION": 0, "RECOGNITION": 0, "SECURITY": 0}
    
    for i, ans in enumerate(data["answers"]):
        cat = MOTIVATION_QUESTIONS[i]["category"]
        scores[cat] += ans
        counts[cat] += 1
    
    avg = {cat: round(scores[cat]/counts[cat], 1) for cat in scores}
    main = max(avg, key=avg.get)
    names = {"ACHIEVEMENT": "Достижение", "POWER": "Власть", "AFFILIATION": "Причастность", 
             "RECOGNITION": "Признание", "SECURITY": "Безопасность"}
    descriptions = {
        "ACHIEVEMENT": "Вы стремитесь к успеху, результатам и совершенству.",
        "POWER": "Вы хотите влиять, управлять и контролировать.",
        "AFFILIATION": "Вы цените общение, дружбу и принадлежность к группе.",
        "RECOGNITION": "Вы хотите быть оцененным и уважаемым.",
        "SECURITY": "Вы цените стабильность, защищенность и порядок."
    }
    
    result = f"🔥 *Результат мотивационного теста*\n\n"
    result += f"Ваш ведущий мотив: *{names[main]}* ({avg[main]}/5)\n\n"
    result += f"{descriptions[main]}\n\n"
    result += f"📊 Все мотивы:\n"
    for k, v in avg.items():
        result += f"• {names[k]}: {v}/5\n"
    
    await message.answer(result, parse_mode="Markdown")
    await message.answer(
        "✅ Тест завершен! Выберите другой тест из меню 👇",
        reply_markup=get_main_menu()
    )
    del user_data[user_id]

async def finish_programming_test(message: types.Message, user_id):
    data = user_data[user_id]
    correct = 0
    for i, ans in enumerate(data["answers"]):
        if ans == PROGRAMMING_QUESTIONS[i]["correct"]:
            correct += 1
    
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
    result += f"Правильных ответов: *{correct} из {total}* ({percent}%)\n\n"
    result += level
    
    await message.answer(result, parse_mode="Markdown")
    await message.answer(
        "✅ Тест завершен! Выберите другой тест из меню 👇",
        reply_markup=get_main_menu()
    )
    del user_data[user_id]

# ==================== ЗАПУСК ====================
async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())