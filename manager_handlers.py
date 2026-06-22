import telebot
from telebot import types
import stats
from config import ALL_MANAGER_IDS, MANAGER_IDS

BACK_BTN = "◀️ Артқа"

def get_manager_name(uid):
    for name, id_ in MANAGER_IDS.items():
        if id_ == uid:
            return name
    return None

def show_manager_menu(bot_instance, chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📊 Бүгінгі отчет"),
        types.KeyboardButton("📅 Аралық отчет"),
        types.KeyboardButton("📋 Барлық уақыт отчеті"),
    )
    bot_instance.send_message(chat_id, "👋 Менеджер панелі", reply_markup=markup)

def send_request_to_manager(bot_instance, manager_id, msg_text, req_no, manager_name):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📞 Байланыстым", callback_data=f"contacted_{req_no}_{manager_name}"))
    try:
        bot_instance.send_message(manager_id, msg_text, reply_markup=markup)
    except Exception as e:
        print(f"Менеджерге жіберу қатесі: {e}")

def register_manager_handlers(bot_instance):
    @bot_instance.callback_query_handler(func=lambda c: c.data.startswith("contacted_"))
    def on_contacted(call):
        parts = call.data.split("_", 2)
        req_no, manager_name = parts[1], parts[2]
        stats.manager_contacted(manager_name)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Шешілді", callback_data=f"resolved_{req_no}_{manager_name}"))
        try:
            bot_instance.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            bot_instance.answer_callback_query(call.id, "✅ Байланыс белгіленді!")
        except:
            bot_instance.answer_callback_query(call.id, "Белгіленді")

    @bot_instance.callback_query_handler(func=lambda c: c.data.startswith("resolved_"))
    def on_resolved(call):
        parts = call.data.split("_", 2)
        req_no, manager_name = parts[1], parts[2]
        stats.manager_resolved(manager_name)
        for req in stats.requests_log:
            if str(req.get("req_no")) == str(req_no):
                req["status"] = "resolved"
                break
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Шешілді ✓", callback_data="done"))
        try:
            bot_instance.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            bot_instance.answer_callback_query(call.id, "✅ Шешілді!")
        except:
            bot_instance.answer_callback_query(call.id, "Белгіленді")

    @bot_instance.callback_query_handler(func=lambda c: c.data == "done")
    def on_done(call):
        bot_instance.answer_callback_query(call.id, "Бұл өтініш бұрын шешілді.")

    @bot_instance.message_handler(func=lambda m: m.chat.id in ALL_MANAGER_IDS and m.text.strip() == "📊 Бүгінгі отчет")
    def manager_today(m):
        name = get_manager_name(m.chat.id)
        if not name: return
        rep = stats.get_manager_report(name, stats.today())
        if not rep:
            bot_instance.send_message(m.chat.id, "Бүгін өтініш жоқ.")
            return
        bot_instance.send_message(m.chat.id, _format_report(name, stats.today(), rep))

    @bot_instance.message_handler(func=lambda m: m.chat.id in ALL_MANAGER_IDS and m.text.strip() == "📋 Барлық уақыт отчеті")
    def manager_all(m):
        name = get_manager_name(m.chat.id)
        if not name: return
        rep = stats.get_manager_report(name)
        if not rep or rep["received"] == 0:
            bot_instance.send_message(m.chat.id, "Әлі өтініш жоқ.")
            return
        bot_instance.send_message(m.chat.id, _format_report(name, "Барлық уақыт", rep))

    @bot_instance.message_handler(func=lambda m: m.chat.id in ALL_MANAGER_IDS and m.text.strip() == "📅 Аралық отчет")
    def manager_range(m):
        msg = bot_instance.send_message(m.chat.id, "📅 Аралықты жаз (мысалы: 01.06.2026-20.06.2026)")
        bot_instance.register_next_step_handler(msg, _handle_range, m.chat.id)

    def _handle_range(message, chat_id):
        name = get_manager_name(chat_id)
        if not name: return
        try:
            d_from, d_to = message.text.strip().split("-")
            d_from, d_to = d_from.strip(), d_to.strip()
            rep = stats.get_manager_report_range(name, d_from, d_to)
            if not rep or rep["received"] == 0:
                bot_instance.send_message(chat_id, "Бұл аралықта өтініш жоқ.")
                return
            bot_instance.send_message(chat_id, _format_report(name, f"{d_from} – {d_to}", rep))
        except:
            bot_instance.send_message(chat_id, "⚠️ Қате формат! Қайталап көріңіз.")

def _format_report(name, period, rep):
    lines = [
        f"📊 Отчет: {name}",
        f"🗓 Кезең: {period}",
        f"─────────────────",
        f"📨 Түскен: {rep['received']}",
        f"📞 Байланысты: {rep['contacted']}",
        f"🔕 Байланыспады: {rep['received'] - rep['contacted']}",
        f"✅ Шешілді: {rep['resolved']}",
    ]
    if rep.get("requests"):
        lines.append("\n📋 Соңғы өтініштер:")
        for i, r in enumerate(rep["requests"][-10:], 1):
            lines.append(f"  {i}. №{r.get('req_no','-')} | {r.get('subject','-')} | {r.get('name','-')} | {r.get('time','-')}")
    return "\n".join(lines)