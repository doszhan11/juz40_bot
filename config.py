TOKEN = "8944602217:AAGzWmFEzn09BDkWXk0xu7fqIZgbPJnzwv4"
ADMIN_ID = 0

FILE_CALENDAR    = "files/Талапкер_күнтізбесі.pdf"
FILE_4CHOICE     = "files/4_ТАҢДАУ_ЖАСАУ_ТЕХНИКАСЫ.pdf"
FILE_CONVERSION  = "files/КОНВЕРТАЦИЯ.pdf"
FILE_GRANT_BALLS = "files/ӨТКЕН_ЖЫЛҒЫ_ГРАНТ_БАЛДАРЫ.pdf"
FILE_GRANT_TYPES = "files/грант_түрлері.pdf"
FILE_SPEC_EXAM   = "files/Арнаулы_емтихан.pdf"
FILE_CREATIVE    = "files/шығармашылық_емтихандар.pdf"
FILE_QUOTA       = "files/квота_түрлері.pdf"

WORK_HOURS = "🕐 Жұмыс уақыты:\nДүйсенбі–Жұма: 13:00–19:00\nСенбі: 11:00–17:00\nЖексенбі: демалыс"

SUBJECT_MANAGERS = {
    "ДЖТ-ENG":   [("Айшуақ Садық", "@shuaq140", 6867690141)],
    "ГЕО-ENG":   [("Айшуақ Садық", "@shuaq140", 6867690141)],
    "БИО-ХИМ":   [("Жанат Арайлым", "@arailymzhanatova", 6851690016),
                  ("Қайбулла Мерей", "@mereykaybulla", 882321084)],
    "ФИЗ-ХИМ":   [("Жанат Арайлым", "@arailymzhanatova", 6851690016),
                  ("Қайбулла Мерей", "@mereykaybulla", 882321084)],
    "ДЖТ-ГЕО":   [("Аблимитов Арманжан", "@sxbepker", 5507966183)],
    "ГЕО-МАТ":   [("Сарсенова Аяжан", "@aayazhann_s", 1167941639)],
    "ФИЗ-МАТ":   [("Тұрарова Аруна", "@arunaturar", 1105856841),
                  ("Орынбек Меруерт", "@meruert_juz40", 0)],
    "ӘДЕБ-ТІЛ":  [("Шанжархан Назерке", "@naz_erkemmm", 1016737548)],
    "ИНФО-МАТ":  [("Мұса Дариға", "@darigamussa", 7364422222)],
    "ДЖТ-ҚҰҚЫҚ": [("Қайырбек Ардан", "@ardddvn", 8595146652)],
    "РУС-ЛИТ":   [("Айдар Гаухария", "@aidar_gaukhariya", 8819455298)],
    "БИО-ГЕО":   [("Тлекбаева Альбина", "@tallbyna", 1727473222)],
}
CREATIVE_MANAGERS = [("Бегалы Алтынай", "@altynai_begali7", 7921367924)]
TURBO_MANAGERS    = [("Жасұланқызы Жасмин", "@jasmin_jasulan", 964748295)]

MANAGER_IDS = {}
for managers in SUBJECT_MANAGERS.values():
    for name, uname, uid in managers:
        if uid:
            MANAGER_IDS[name] = uid
            MANAGER_IDS[uname] = uid
for name, uname, uid in CREATIVE_MANAGERS + TURBO_MANAGERS:
    if uid:
        MANAGER_IDS[name] = uid
        MANAGER_IDS[uname] = uid

ALL_MANAGER_IDS = set(MANAGER_IDS.values())

ADMIN_IDS = {1222061568, 6479767513}

COURSES = ["SMART", "GENIUS", "TURBO"]
SUBJECT_LIST = list(SUBJECT_MANAGERS.keys()) + ["Шығармашылық"]

SECTIONS = [
    "1. Грант конкурсы және құжаттар",
    "2. Грант сандары 2026",
    "3. Грант шектік балл 2025-2026",
    "4. Халықаралық сертификаттар және КазТЕСТ",
    "5. Талапкер күнтізбесі 2026",
    "6. Грант конкурсы 4 таңдау техникасы",
    "7. Мамандықтар кітапшасы",
    "8. Арнаулы емтихан",
    "9. Квота түрлері",
    "10. Грант түрлері",
    "11. Шығармашылық емтихандар",
    "12. Call центр қызметімен байланысу",
]