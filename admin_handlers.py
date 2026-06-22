from telebot import types
import stats
import traceback
from config import ADMIN_IDS, MANAGER_IDS
from manager_handlers import _format_report

def register_admin_handlers(bot_instance):
    
    def show_admin_menu(chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("📊 Бүгінгі жалпы отчет"),
            types.KeyboardButton("📅 Аралық жалпы отчет"),
            types.KeyboardButton("👤 Менеджер отчеті"),
            types.KeyboardButton("📋 Барлық уақыт"),
        )
        bot_instance.send_message(chat_id, "👑 Админ панелі", reply_markup=markup)

    @bot_instance.message_handler(func=lambda m: m.chat.id in ADMIN_IDS and m.text.strip() == "📊 Бүгінгі жалпы отчет")
    def admin_today(m):
        try:
            bot_instance.send_message(m.chat.id, _build_general_report(stats.today()))
        except Exception as e:
            bot_instance.send_message(m.chat.id, f"❌ Қате: {e}")

    @bot_instance.message_handler(func=lambda m: m.chat.id in ADMIN_IDS and m.text.strip() == "📋 Барлық уақыт")
    def admin_all(m):
        try:
            bot_instance.send_message(m.chat.id, _build_general_report(None))
        except Exception as e:
            bot_instance.send_message(m.chat.id, f"❌ Қате: {e}")

    @bot_instance.message_handler(func=lambda m: m.chat.id in ADMIN_IDS and m.text.strip() == "📅 Аралық жалпы отчет")
    def admin_range(m):
        msg = bot_instance.send_message(m.chat.id, "📅 Аралықты жаз (мысалы: 01.06.2026-20.06.2026)")
        bot_instance.register_next_step_handler(msg, _admin_range_handler, m.chat.id)

    def _admin_range_handler(message, chat_id):
        try:
            parts = message.text.strip().split("-")
            if len(parts) != 2:
                bot_instance.send_message(chat_id, "⚠️ Қате формат!")
                return
            date_from, date_to = parts[0].strip(), parts[1].strip()
            bot_instance.send_message(chat_id, _build_range_report(date_from, date_to))
        except Exception as e:
            bot_instance.send_message(chat_id, f"❌ Қате: {e}")

    @bot_instance.message_handler(func=lambda m: m.chat.id in ADMIN_IDS and m.text.strip() == "👤 Менеджер отчеті")
    def admin_manager_list(m):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for name in MANAGER_IDS:
            if not name.startswith("@"):
                markup.add(types.KeyboardButton(f"👤 {name}"))
        markup.add(types.KeyboardButton("◀️ Артқа"))
        bot_instance.send_message(m.chat.id, "Менеджерді таңдаңыз:", reply_markup=markup)

    @bot_instance.message_handler(func=lambda m: m.chat.id in ADMIN_IDS and m.text.startswith("👤 "))
    def admin_manager_detail(m):
        name = m.text.replace("👤 ", "").strip()
        if name.startswith("@"):
            name = name[1:]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton(f"📊 Бүгін {name}"),
            types.KeyboardButton(f"📋 Барлығы {name}"),
            types.KeyboardButton("◀️ Артқа"),
        )
        bot_instance.send_message(m.chat.id, f"Менеджер: {name}", reply_markup=markup)

    @bot_instance.message_handler(func=lambda m: m.chat.id in ADMIN_IDS and m.text.startswith("📊 Бүгін "))
    def admin_manager_today(m):
        try:
            name = m.text.replace("📊 Бүгін ", "").strip()
            if name.startswith("@"):
                name = name[1:]
            rep = stats.get_manager_report(name, stats.today())
            if not rep:
                bot_instance.send_message(m.chat.id, f"{name} бүгін өтініш жоқ.")
                return
            bot_instance.send_message(m.chat.id, _format_report(name, stats.today(), rep))
        except Exception as e:
            bot_instance.send_message(m.chat.id, f"❌ Қате: {e}")

    @bot_instance.message_handler(func=lambda m: m.chat.id in ADMIN_IDS and m.text.startswith("📋 Барлығы "))
    def admin_manager_all(m):
        try:
            name = m.text.replace("📋 Барлығы ", "").strip()
            if name.startswith("@"):
                name = name[1:]
            rep = stats.get_manager_report(name)
            if not rep or rep["received"] == 0:
                bot_instance.send_message(m.chat.id, f"{name} өтініш жоқ.")
                return
            bot_instance.send_message(m.chat.id, _format_report(name, "Барлық уақыт", rep))
        except Exception as e:
            bot_instance.send_message(m.chat.id, f"❌ Қате: {e}")

    @bot_instance.message_handler(func=lambda m: m.chat.id in ADMIN_IDS and m.text.strip() == "◀️ Артқа")
    def admin_back(m):
        show_admin_menu(m.chat.id)

    return show_admin_menu

def _build_general_report(date_str=None):
    try:
        d = stats.data
        period = date_str if date_str else "Барлық уақыт"
        lines = [
            f"📊 Жалпы отчет — {period}",
            f"─────────────────",
            f"👥 Жалпы запрос: {d.get('total_users', 0)}",
            f"📨 Менеджерге жіберілді: {d.get('to_manager', 0)}",
            f"✅ Шешілді: {d.get('resolved', 0)}",
            f"❌ Шешілмеді: {d.get('unresolved', 0)}",
        ]
        if d.get("by_section"):
            lines.append("\n📂 Бөлімдер бойынша:")
            for sec, v in d["by_section"].items():
                if v.get("total", 0) > 0:
                    short = sec.split(". ", 1)[-1] if ". " in sec else sec
                    lines.append(f"  • {short}: {v['total']} (✅{v.get('resolved',0)} / ❌{v.get('unresolved',0)})")
        if d.get("by_subject"):
            lines.append("\n📚 Пәндер бойынша:")
            for subj, cnt in d["by_subject"].items():
                if cnt > 0:
                    lines.append(f"  • {subj}: {cnt}")
        if d.get("by_course"):
            lines.append("\n🎓 Курс бойынша:")
            for course, cnt in d["by_course"].items():
                if cnt > 0:
                    lines.append(f"  • {course}: {cnt}")
        lines.append("\n👤 Менеджерлер бойынша:")
        for uname in stats.manager_stats:
            rep = stats.get_manager_report(uname, date_str) if date_str else stats.get_manager_report(uname)
            if rep and rep.get("received", 0) > 0:
                lines.append(f"  {uname}: {rep['received']} өтініш, байланысты: {rep.get('contacted',0)}, шешілді: {rep.get('resolved',0)}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Отчет құру кезінде қате: {e}"

def _build_range_report(date_from, date_to):
    try:
        lines = [f"📊 Аралық отчет: {date_from} – {date_to}", "─────────────────"]
        lines.append("👤 Менеджерлер бойынша:")
        for uname in stats.manager_stats:
            rep = stats.get_manager_report_range(uname, date_from, date_to)
            if rep and rep.get("received", 0) > 0:
                lines.append(f"  {uname}: {rep['received']} өтініш, байланысты: {rep.get('contacted',0)}, шешілді: {rep.get('resolved',0)}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Отчет құру кезінде қате: {e}"