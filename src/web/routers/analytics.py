"""Analytics reports and infographics metadata endpoints."""

from typing import Any

from fastapi import APIRouter

from src.core.config import settings

router_analytics = APIRouter(prefix="/api", tags=["analytics"])


@router_analytics.get("/infographics")
def list_infographics() -> dict[str, Any]:
    """Return available infographics grouped by analytical categories."""
    categories: dict[str, Any] = {
        "dashboard": {
            "title": "Головне та базова інфографіка",
            "items": [
                {"file": "wordcloud.png", "title": "Хмара слів", "desc": "Візуалізація найчастіших змістовних слів за весь час"},
                {"file": "top_words.png", "title": "Топ-25 змістовних слів", "desc": "Рейтинг найбільш вживаних лексичних одиниць"},
                {"file": "years_volume.png", "title": "Обсяг за роками", "desc": "Динаміка кількості повідомлень та слів"},
                {"file": "ttr_evolution.png", "title": "Багатство мови (TTR)", "desc": "Словникове різноманіття та середня довжина реплік"},
                {"file": "zipf_distribution.png", "title": "Закон Ціпфа", "desc": "Рангочастотний розподіл слів vs ідеальний закон"},
                {"file": "word_length_distribution.png", "title": "Довжина слів", "desc": "Розподіл слів за кількістю літер"},
            ],
        },
        "time": {
            "title": "Часові патерни, ритм та режим сну",
            "items": [
                {"file": "timeline_monthly.png", "title": "Щомісячний таймлайн", "desc": "Обсяг повідомлень місяць за місяцем за всі роки"},
                {"file": "activity_by_hour.png", "title": "Активність за годинами", "desc": "Добовий розподіл відправки повідомлень"},
                {"file": "activity_by_weekday.png", "title": "Активність за днями тижня", "desc": "Порівняння робочих днів та вихідних"},
                {"file": "seasonality.png", "title": "Сезонність", "desc": "У які місяці року інтенсивність спілкування найвища"},
                {"file": "night_trend.png", "title": "Нічні повідомлення", "desc": "Частка повідомлень після півночі (00:00–06:00)"},
                {"file": "active_days.png", "title": "Активні дні та серії", "desc": "Кількість активних днів на рік та рекорди поспіль"},
                {"file": "sleep_evolution.png", "title": "Еволюція режиму сну", "desc": "Реконструкція часу засинання, пробудження та тривалості сну"},
                {"file": "message_rhythm.png", "title": "Ритм та паузи", "desc": "Розподіл пауз між репліками та частка повідомлень-черг"},
                {"file": "msg_length_dist.png", "title": "Розподіл довжини реплік", "desc": "Гістограма довжини повідомлень у словах"},
            ],
        },
        "style": {
            "title": "Стиль мовлення, словник та лінгвістика",
            "items": [
                {"file": "core_vocabulary.png", "title": "Кістяк мовлення", "desc": "Слова, що стабільно вживаються з року в рік (heatmap)"},
                {"file": "vocab_timeline.png", "title": "Чесний ріст словника", "desc": "Крива накопичення перевірених та словникових лем"},
                {"file": "vocab_growth.png", "title": "Закон Хіпса", "desc": "Зростання словникового запасу від обсягу тексту"},
                {"file": "vocab_validation.png", "title": "Склад словника", "desc": "Словникові слова vs латиниця vs сленг/одруківки"},
                {"file": "ngrams.png", "title": "Коронні фрази", "desc": "Топ стійких біграм та триграм"},
                {"file": "pos_evolution.png", "title": "Частини мови", "desc": "Співвідношення дієслів, іменників, прикметників"},
                {"file": "informality.png", "title": "Неформальність", "desc": "Частка несловникових слів та сленгу за роками"},
                {"file": "laughter_evolution.png", "title": "Еволюція сміху", "desc": "Динаміка написання сміху (ха-ха, хпхвх, хехе)"},
                {"file": "questions_exclamations.png", "title": "Питання та знаки оклику", "desc": "Емоційність та частка повідомлень із ? та !"},
                {"file": "profanity_trend.png", "title": "Частота мату", "desc": "Ненормативна лексика на 1000 слів за роками"},
                {"file": "language_mix.png", "title": "Мовний мікс", "desc": "Співвідношення мов (українська / російська / англійська)"},
            ],
        },
        "social": {
            "title": "Стосунки, чати та кластеризація",
            "items": [
                {"file": "top_chats.png", "title": "Топ діалогів", "desc": "Найбільш активні чати за кількістю повідомлень"},
                {"file": "streamgraph_chats.png", "title": "Потік спілкування (Streamgraph)", "desc": "Як з роками перерозподілялась увага між чатами"},
                {"file": "social_breadth.png", "title": "Широта спілкування", "desc": "Кількість співрозмовників на місяць та частка топ-3"},
                {"file": "relationships_timeline.png", "title": "Таймлайн життя чатів", "desc": "Коли починалось, спалахувало та згасало спілкування"},
                {"file": "chat_fingerprint.png", "title": "Лінгвістичні відбитки чатів", "desc": "Характерні слова для кожного контакту (TF-IDF)"},
                {"file": "ty_vy.png", "title": "Ти / Ви", "desc": "Рівень формальності та пропорція звертань"},
                {"file": "mat_per_chat.png", "title": "Мат за чатами", "desc": "Розподіл ненормативної лексики по конкретних діалогах"},
                {"file": "speech_clustering.png", "title": "Кластеризація мовлення", "desc": "Дендрограма схожості лексичного стилю з різними людьми"},
            ],
        },
    }

    # Filter out files that do not exist yet on disk using list comprehension
    for category in categories.values():
        category["items"] = [
            item for item in category["items"]
            if (settings.dir_infographics / item["file"]).exists()
        ]

    return categories


@router_analytics.get("/report")
def get_report() -> dict[str, Any]:
    """Return generated textual report content or indicate absence."""
    if settings.file_report.exists():
        with open(settings.file_report, encoding="utf-8") as file_handle:
            return {"exists": True, "content": file_handle.read()}
    return {"exists": False, "content": None}
