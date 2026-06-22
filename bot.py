import telebot
from telebot import types
import threading
import time
from datetime import datetime
import os
import stats
from config import *
from manager_handlers import register_manager_handlers, send_request_to_manager, show_manager_menu
from admin_handlers import register_admin_handlers

bot = telebot.TeleBot(TOKEN)

user_state = {}
BACK_BTN = "◀️ Артқа"
_manager_turn = {}
processing = set()

SECTION_DATA = {
    "1. Грант конкурсы және құжаттар": {
        "text": "👋 Сәлем, талапкер!\n\n📆 Грант конкурсына құжаттар қабылдау 13–20 шілде аралығында жүзеге асырылады.\n\n📑 Офлайн (ЖОО қабылдау комиссиясы), онлайн виртуалды немесе eGov арқылы тапсыруға болады.\n\n✅ Қажетті құжаттар:\n✔️ жеке куәлік\n✔️ ҰБТ сертификаты\n✔️ 3×4 фото\n✔️ аттестат немесе диплом (колледж үшін)\n✔️ жеңілдетілген санат бойынша растайтын құжат (бар болса)\n✔️ B167 мамандығы үшін — медициналық куәландыру\n\nℹ️ Қосымша ақпарат бойынша ЖОО қабылдау комиссияларына хабарласыңыз.",
        "file": None,
    },
    "2. Грант сандары 2026": {
        "text": "👋 Сәлем, талапкер!\n\n📊 2025-2026 грант саны:\nhttps://testcenter.kz/?page_id=45090",
        "file": None,
    },
    "3. Грант шектік балл 2025-2026": {
        "text": "👋 Сәлем, талапкер!\n\nӨткен жылғы шектік баллдар төмендегі файлда 👇",
        "file": FILE_GRANT_BALLS,
    },
    "4. Халықаралық сертификаттар және КазТЕСТ": {
        "text": "👋 Сәлем, талапкер!\n\nХалықаралық сертификаттар мен КазТЕСТ конвертациясы 👇",
        "file": FILE_CONVERSION,
    },
    "5. Талапкер күнтізбесі 2026": {
        "text": "👋 Сәлем, талапкер!\n\nТалапкер күнтізбесі 2026 👇",
        "file": FILE_CALENDAR,
    },
    "6. Грант конкурсы 4 таңдау техникасы": {
        "text": "👋 Сәлем, талапкер!\n\n4 таңдау жасау техникасы 👇",
        "file": FILE_4CHOICE,
    },
    "7. Мамандықтар кітапшасы": {
        "text": "👋 Сәлем, талапкер!\n\n📚 Мамандықтар кітапшасы және аналитика:\nhttps://drive.google.com/drive/folders/1RwuFYl4rd_LWDe9iciaMPUQXdhRZDEMQ?usp=sharing",
        "file": None,
    },
    "8. Арнаулы емтихан": {
        "text": "👋 Сәлем, талапкер!\n\n📆 Арнаулы емтихандар 20 маусым – 20 тамыз аралығында ЖОО-ларда өткізіледі (онлайн/офлайн).\n\n📌 Грантқа да, ақылы оқуға да міндетті. Грантқа тапсырар алдында өтіңіз.\n\n✅❌ Нәтиже «өтті»/«өтпеді» — сол күні жарияланады.\n\n👩‍🏫👨‍⚕️ Педагогикалық + медициналық мамандыққа тапсырсаңыз — екі бағытта да тапсырыңыз.\n\nℹ️ Онлайн форматтағы ЖОО тізімі файлда 👇",
        "file": FILE_SPEC_EXAM,
    },
    "9. Квота түрлері": {
        "text": "👋 Сәлем, талапкер!\n\nКвота түрлері файлда 👇",
        "file": FILE_QUOTA,
    },
    "10. Грант түрлері": {
        "text": "👋 Сәлем, талапкер!\n\nГрант түрлері файлда 👇",
        "file": FILE_GRANT_TYPES,
    },
    "11. Шығармашылық емтихандар": {
        "text": "👋 Сәлем, талапкер!\n\nШығармашылық емтихандар туралы файлда 👇",
        "file": FILE_CREATIVE,
    },
    "12. Call центр қызметімен байланысу": {
        "text": None,
        "file": None,
    },
}

def pick_manager(course, subject, section):
    if subject == "Шығармашылық":
        candidates = CREATIVE_MANAGERS
    elif course == "TURBO":
        candidates = TURBO_MANAGERS
    elif "шығармашылық" in section.lower() or section == "11. Шығармашылық емтихандар":
        candidates = CREATIVE_MANAGERS
    else:
        candidates = SUBJECT_MANAGERS.get(subject, TURBO_MANAGERS)
    
    if len(candidates) == 1:
        return candidates[0][0], candidates[0][2]
    
    key = subject or section
    idx = _manager_turn.get(key, 0) % len(candidates)
    _manager_turn[key] = idx + 1
    return candidates[idx][0], candidates[idx][2]

def send_file_safe(chat_id, path, caption=""):
    if not path or not os.path.exists(path):
        return
    try:
        with open(path, "rb") as f:
            bot.send_chat_action(chat_id, 'upload_document')
            bot.send_document(chat_id, f, caption=caption)
    except Exception as e:
        print(f"Файл қатесі: {e}")

WELCOME_TEXT = (
    "👋 Сәлем, байланыста juz40_career!\n\n"
    "Сіздің сұрақтарыңызға толық жауап беріп, 4 таңдауға кеңес береміз.\n\n"
    "⚠️ Ескерту: Грант конкурсына өтініш білдіру кезінде 4 мамандық таңдау "
    "рұқсат етіледі және жауапкершілік сізде, біздің ақпараттарды кеңес "
    "құралы ретінде пайдалана аласыз. Сәттілік!\n\n"
    "👇 Төмендегі батырмалар арқылы мәселеңізді анықтасақ:\n\n"
    "👇 Курсыңызды таңдаңыз:"
)

def send_welcome(chat_id):
    bot.send_message(chat_id, WELCOME_TEXT)

def screen_start(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(*[types.KeyboardButton(c) for c in COURSES])
    bot.send_message(chat_id, "👇 Курсыңызды таңдаңыз:", reply_markup=markup)

def screen_section(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for s in SECTIONS:
        markup.add(types.KeyboardButton(s))
    markup.add(types.KeyboardButton(BACK_BTN))
    bot.send_message(chat_id, "📂 Мәселе бөлімін таңдаңыз:", reply_markup=markup)

def screen_subject(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for s in SUBJECT_LIST:
        markup.add(types.KeyboardButton(s))
    markup.add(types.KeyboardButton(BACK_BTN))
    bot.send_message(chat_id, "📚 Пәніңізді таңдаңыз:", reply_markup=markup)

def screen_helpful(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("✅ Иә"), types.KeyboardButton("❌ Жоқ"))
    markup.add(types.KeyboardButton(BACK_BTN))
    bot.send_message(chat_id, "Мәселе шешімін таба алдыңыз ба?", reply_markup=markup)

def ask_name(chat_id):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "👤 Аты-жөніңізді жазыңыз:", reply_markup=markup)

def ask_ubt(chat_id):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "📊 ҰБТ-да жинаған ең жоғары балыңыз:", reply_markup=markup)

def ask_region(chat_id):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "🌍 Мектеп бітірген өңіріңіз:", reply_markup=markup)

def ask_quota(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(types.KeyboardButton("Бар"), types.KeyboardButton("Жоқ"), types.KeyboardButton("Нақтылағым келеді"))
    bot.send_message(chat_id, "🏘️ Ауылдық квотаңыз бар ма?\n(Білмесеңіз — «Нақтылағым келеді»)", reply_markup=markup)

def ask_question(chat_id):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "✍️ Сұрағыңызды толық жазыңыз:", reply_markup=markup)

def ask_phone(chat_id):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "📞 Телефон нөміріңізді жазыңыз\n(болмаса «-» деп өткізіңіз)", reply_markup=markup)

def show_ask_again_button(chat_id, extra_text=""):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("❓ Сұрағым бар"))
    if extra_text:
        bot.send_message(chat_id, extra_text, reply_markup=markup)
    else:
        bot.send_message(chat_id, "Басқа сұрағыңыз бар ма?", reply_markup=markup)

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    if chat_id in ADMIN_IDS:
        show_admin_menu = register_admin_handlers(bot)
        show_admin_menu(chat_id)
        return
    if chat_id in ALL_MANAGER_IDS:
        show_manager_menu(bot, chat_id)
        return
    user_state[chat_id] = {"history": []}
    stats.data["total_users"] += 1
    send_welcome(chat_id)
    screen_start(chat_id)

# ★ БАСТЫ ХЕНДЛЕР ТЕК ПАЙДАЛАНУШЫЛАР ҮШІН ҒАНА
@bot.message_handler(func=lambda m: m.chat.id not in ADMIN_IDS and m.chat.id not in ALL_MANAGER_IDS)
def handle(message):
    chat_id = message.chat.id
    text = message.text.strip() if message.text else ""

    if chat_id in processing:
        return

    processing.add(chat_id)

    try:
        state = user_state.get(chat_id, {"history": []})
        history = state.get("history", [])

        if text == "❓ Сұрағым бар":
            user_state[chat_id] = {"history": []}
            send_welcome(chat_id)
            screen_start(chat_id)
            return

        if text == BACK_BTN:
            if not history:
                screen_start(chat_id)
                user_state[chat_id] = {"history": []}
                return

            last = history.pop()
            state["history"] = history

            if last in ("ask_name", "ask_ubt", "ask_region", "ask_quota", "ask_question", "ask_phone"):
                for k in ("step","name","ubt","region","quota","question","phone","manager_uname","manager_id"):
                    state.pop(k, None)
                state.pop("section", None)
                state.pop("subject", None)
                user_state[chat_id] = state
                screen_section(chat_id)
                return

            if last == "course":
                screen_start(chat_id)
                user_state[chat_id] = {"history": []}
                return
            elif last == "section":
                state.pop("section", None)
                user_state[chat_id] = state
                screen_section(chat_id)
                return
            elif last in ("subject", "subject_for_manager"):
                state.pop("subject", None)
                state.pop("manager_uname", None)
                state.pop("manager_id", None)
                state.pop("step", None)
                user_state[chat_id] = state
                screen_section(chat_id)
                return
            elif last == "answer":
                state.pop("section", None)
                user_state[chat_id] = state
                screen_section(chat_id)
                return
            else:
                screen_section(chat_id)
                user_state[chat_id] = state
            return

        if text in COURSES and "course" not in state:
            state["course"] = text
            state["history"] = ["course"]
            user_state[chat_id] = state
            stats.inc_course(text)
            screen_section(chat_id)
            return

        if text in SECTIONS and "section" not in state:
            state["section"] = text
            state["history"] = ["course", "section"]
            user_state[chat_id] = state
            stats.inc_section(text)

            if text == "12. Call центр қызметімен байланысу":
                state["history"].append("subject")
                user_state[chat_id] = state
                screen_subject(chat_id)
                return

            sec_data = SECTION_DATA.get(text)
            if sec_data and sec_data["text"]:
                bot.send_message(chat_id, sec_data["text"])
                if sec_data["file"]:
                    send_file_safe(chat_id, sec_data["file"])
            state["history"].append("answer")
            user_state[chat_id] = state
            screen_helpful(chat_id)
            return

        if text == "✅ Иә" and state.get("section"):
            stats.inc_resolved_section(state["section"])
            show_ask_again_button(
                chat_id,
                "Мәселе шешілгеніне қуаныштымын! Грант жағасына бірге жүзейік! ❤️"
            )
            user_state[chat_id] = {"history": []}
            return

        if text == "❌ Жоқ" and state.get("section"):
            stats.inc_unresolved_section(state["section"])
            bot.send_message(chat_id, "Кешірім сұраймыз! Менеджерге жалғастырайық.\nПәніңізді таңдаңыз:")
            state["history"].append("subject_for_manager")
            user_state[chat_id] = state
            screen_subject(chat_id)
            return

        if text in SUBJECT_LIST and "subject" not in state:
            state["subject"] = text
            stats.inc_subject(text)
            m_name, m_id = pick_manager(state.get("course", ""), text, state.get("section", ""))
            state["manager_uname"] = m_name
            state["manager_id"] = m_id
            state["step"] = "ask_name"
            state["history"].append("subject")
            user_state[chat_id] = state
            bot.send_message(chat_id, f"✅ Пән: {text}\nМенеджер: {m_name}")
            ask_name(chat_id)
            return

        if not state.get("course"):
            send_welcome(chat_id)
            screen_start(chat_id)
            user_state[chat_id] = {"history": []}
            return

        if not state.get("section"):
            bot.send_message(chat_id, "⚠️ Алдымен проблема бөлімін таңдаңыз!")
            screen_section(chat_id)
            return

        step = state.get("step")
        if step == "ask_name":
            state["name"] = text
            state["step"] = "ask_ubt"
            state["history"].append("ask_name")
            user_state[chat_id] = state
            ask_ubt(chat_id)
            return
        if step == "ask_ubt":
            state["ubt"] = text
            state["step"] = "ask_region"
            state["history"].append("ask_ubt")
            user_state[chat_id] = state
            ask_region(chat_id)
            return
        if step == "ask_region":
            state["region"] = text
            state["step"] = "ask_quota"
            state["history"].append("ask_region")
            user_state[chat_id] = state
            ask_quota(chat_id)
            return
        if step == "ask_quota":
            state["quota"] = text
            state["step"] = "ask_question"
            state["history"].append("ask_quota")
            user_state[chat_id] = state
            ask_question(chat_id)
            return
        if step == "ask_question":
            state["question"] = text
            state["step"] = "ask_phone"
            state["history"].append("ask_question")
            user_state[chat_id] = state
            ask_phone(chat_id)
            return
        if step == "ask_phone":
            tg_username = message.from_user.username
            tg_link = f"@{tg_username}" if tg_username else "username жоқ"
            phone = text if text != "-" else (tg_link if tg_username else "Белгісіз")

            req_no = stats.next_req_no()
            m_name = state.get("manager_uname", "Белгісіз")
            m_id = state.get("manager_id", 0)
            section = state.get("section", "—")
            subject = state.get("subject", "—")
            name = state.get("name", "—")
            ubt = state.get("ubt", "—")
            region = state.get("region", "—")
            quota = state.get("quota", "—")
            question = state.get("question", "—")
            course = state.get("course", "—")

            msg = (
                f"📨 Жаңа өтініш №{req_no}\n"
                f"─────────────────\n"
                f"Сұрақ: {question}\n\n"
                f"Аты-жөні: {name}\n"
                f"Курс: {course}\n"
                f"Пән: {subject}\n"
                f"Бөлім: {section}\n"
                f"ҰБТ балл: {ubt}\n"
                f"Өңір: {region}\n"
                f"Ауылдық квота: {quota}\n\n"
                f"Байланыс: {phone}\n"
                f"Telegram: {tg_link}"
            )

            req_info = {
                "req_no": req_no, "user_id": chat_id, "name": name,
                "course": course, "subject": subject, "section": section,
                "ubt": ubt, "region": region, "quota": quota,
                "question": question, "contact": phone, "tg": tg_link,
                "manager": m_name, "status": "open", "time": stats.now_str()
            }
            stats.add_request(req_info)
            stats.manager_received(m_name, {
                "req_no": req_no, "subject": subject, "name": name,
                "ubt": ubt, "time": stats.now_str()
            })

            if m_id:
                send_request_to_manager(bot, m_id, msg, req_no, m_name)
            else:
                print(f"Ескерту: {m_name} ID-і жоқ")

            show_ask_again_button(
                chat_id,
                f"✅ Рахмет, {name}! 🙏\nМенеджер {m_name} жақын арада байланысады.\n\n{WORK_HOURS}"
            )
            user_state[chat_id] = {"history": []}
            return

        bot.send_message(chat_id, "⚠️ Түсініксіз хабарлама. Өтінеміз, дұрыс таңдау жасаңыз.")
        if not state.get("section"):
            screen_section(chat_id)
        else:
            if state.get("step"):
                step = state["step"]
                if step == "ask_name":
                    ask_name(chat_id)
                elif step == "ask_ubt":
                    ask_ubt(chat_id)
                elif step == "ask_region":
                    ask_region(chat_id)
                elif step == "ask_quota":
                    ask_quota(chat_id)
                elif step == "ask_question":
                    ask_question(chat_id)
                elif step == "ask_phone":
                    ask_phone(chat_id)
                else:
                    screen_section(chat_id)
            else:
                screen_section(chat_id)

    finally:
        processing.discard(chat_id)

def build_report():
    from admin_handlers import _build_general_report
    return _build_general_report(stats.today())

def send_report():
    if ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, build_report())
        except Exception as e:
            print(f"Отчет қатесі: {e}")

def schedule_reports():
    sent = set()
    while True:
        now = datetime.now()
        key = (now.date(), now.hour)
        if now.hour in (12, 21) and key not in sent:
            send_report()
            sent.add(key)
            sent = {k for k in sent if k[0] == now.date()}
        time.sleep(30)

register_manager_handlers(bot)
show_admin_menu = register_admin_handlers(bot)

if __name__ == "__main__":
    print("✅ Бот іске қосылды...")
    from web_dashboard import run_dashboard
    threading.Thread(target=schedule_reports, daemon=True).start()
    threading.Thread(target=run_dashboard, kwargs={"port": 5000}, daemon=True).start()
    print("✅ Веб-дашборд іске қосылды: port 5000")
    bot.infinity_polling()