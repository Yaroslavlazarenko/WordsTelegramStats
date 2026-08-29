"""
Pipeline runner and orchestrator.
Executes the full NLP analytics and infographics generation suite with uniform logging.
"""

import time
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from src.analytics.text_stats import (
    analyze_vocabulary_shifts,
    compute_message_stats,
    compute_zipf_comparison,
    safe_filename,
    top_meaningful,
    write_frequency_file,
)
from src.core.config import REPORT_FILE, WORDS_LISTS_DIR
from src.data.loader import load_chats
from src.visualization.basic import generate_basic_charts
from src.visualization.behavioral import generate_behavioral_charts
from src.visualization.linguistic import generate_linguistic_charts
from src.visualization.social import generate_social_charts


def run_text_analysis(log_callback: Callable[[str], None] | None = None, lang: str = "uk") -> dict[str, Any]:
    """
    Runs textual and corpus frequency analysis across chats, years, all-time,
    and generates advanced_report.txt and words_lists/ files.
    """
    is_en = lang == "en"
    lines: list[str] = []

    def log(msg: str = "") -> None:
        lines.append(msg)
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    chats, filt = load_chats()
    if not chats:
        no_data_msg = "[❌] No data found for analysis. Please sync messages first." if is_en else "[❌] Не знайдено даних для аналізу. Спочатку синхронізуйте повідомлення."
        log(no_data_msg)
        return {"status": "no_data"}

    header_title = " ADVANCED TELEGRAM WORD STATS ANALYSIS" if is_en else " РОЗШИРЕНИЙ АНАЛІЗ СТАТИСТИКИ СЛІВ TELEGRAM"
    log("=" * 78)
    log(header_title)
    log("=" * 78)
    if is_en:
        log(f"Dialogues with messages:         {len(chats)}")
        log(f"Total messages inspected:        {filt['total']:>8}")
        log(f"  [-] forwarded (forward):       {filt['forwarded']:>8}")
        log(f"  [-] quotes/copypastes/links:   {filt['noise']:>8}")
        log(f"  [+] clean (author speech):     {filt['clean']:>8}")
    else:
        log(f"Діалогів з повідомленнями:    {len(chats)}")
        log(f"Всього повідомлень переглянуто:{filt['total']:>8}")
        log(f"  [-] пересланих (forward):   {filt['forwarded']:>8}")
        log(f"  [-] цитат/копіпастів/посилань:{filt['noise']:>8}")
        log(f"  [+] чистих (моє мовлення):   {filt['clean']:>8}")

    # 1. За кожним чатом
    log("\n" + "=" * 78)
    log(" 1. СТАТИСТИКА ЗА КОЖНИМ ДІАЛОГОМ")
    log("=" * 78)

    by_chat_dir = WORDS_LISTS_DIR / "by_chat"
    by_chat_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for ch in chats:
        st = compute_message_stats(ch["messages"])
        if st["total_words"] == 0:
            continue
        fname = safe_filename(ch["title"]) + ".txt"
        write_frequency_file(by_chat_dir / fname, ch["title"], st["counter"])
        top3 = ", ".join(w for w, _ in top_meaningful(st["counter"], 3)) or "—"
        rows.append({
            "title": ch["title"],
            "n_msg": st["n_msg"],
            "words": st["total_words"],
            "unique": st["unique"],
            "ttr": st["ttr"],
            "avg": st["avg_words"],
            "top3": top3,
        })

    rows.sort(key=lambda r: r["n_msg"], reverse=True)
    log(f"Проаналізовано діалогів: {len(rows)}")
    log(f"Повні частотні списки за кожним чатом збережено у: {by_chat_dir}/\n")
    log(f"{'#':>3} {'Чат':<24} {'Повідом':>8} {'Слів':>8} {'Унік':>7} {'Різноманіт':>11}  Топ-слова")
    log("-" * 95)
    for i, r in enumerate(rows[:30], 1):
        log(f"{i:>3} {r['title'][:24]:<24} {r['n_msg']:>8} {r['words']:>8} {r['unique']:>7} {r['ttr']*100:>10.1f}%  {r['top3']}")
    if len(rows) > 30:
        log(f"    ... та ще {len(rows) - 30} діалогів (див. файли у {by_chat_dir}/)")

    # 2. За роками
    log("\n" + "=" * 78)
    log(" 2. СТАТИСТИКА ЗА РОКАМИ — ЕВОЛЮЦІЯ СТИЛЮ МОВЛЕННЯ")
    log("=" * 78)

    by_year = defaultdict(list)
    for ch in chats:
        for date_str, text in ch["messages"]:
            if date_str and len(date_str) >= 4 and date_str[:4].isdigit():
                by_year[date_str[:4]].append((date_str, text))

    years = sorted(by_year.keys())
    year_stats = {y: compute_message_stats(by_year[y]) for y in years}

    log(f"\n{'Рік':<6} {'Повідом':>8} {'Слів':>9} {'Унік':>8} {'Різноманіт':>11} {'Слів/повідом':>13} {'Симв/повідом':>13}")
    log("-" * 74)
    for y in years:
        s = year_stats[y]
        log(f"{y:<6} {s['n_msg']:>8} {s['total_words']:>9} {s['unique']:>8} {s['ttr']*100:>10.1f}% {s['avg_words']:>13.1f} {s['avg_chars']:>13.1f}")

    by_year_dir = WORDS_LISTS_DIR / "by_year"
    by_year_dir.mkdir(parents=True, exist_ok=True)
    log("\nТОП-12 ЗМІСТОВНИХ СЛІВ ЗА РОКАМИ:")
    log("-" * 78)
    for y in years:
        s = year_stats[y]
        write_frequency_file(by_year_dir / f"{y}.txt", f"YEAR {y}", s["counter"])
        tops = top_meaningful(s["counter"], 12)
        line = ", ".join(f"{w}({c})" for w, c in tops)
        log(f"{y}: {line}")

    if len(years) >= 2:
        rose, fell = analyze_vocabulary_shifts(year_stats, years)
        if rose:
            log(f"\nСЛОВА, ЩО «УВІЙШЛИ В МОДУ» ({years[0]} → {years[-1]}, частота на млн слів):")
            for w, f1, f2, d in rose[:12]:
                log(f"   {w:<20} {f1:>8.0f} → {f2:>8.0f}   (+{d:.0f})")
        if fell:
            log(f"\nСЛОВА, ЩО «ВИЙШЛИ З МОДИ» ({years[0]} → {years[-1]}):")
            for w, f1, f2, d in fell[:12]:
                log(f"   {w:<20} {f1:>8.0f} → {f2:>8.0f}   ({d:.0f})")

    # 3. За весь час
    log("\n" + "=" * 78)
    log(" 3. СТАТИСТИКА ЗА ВЕСЬ ЧАС")
    log("=" * 78)

    all_msgs = [m for ch in chats for m in ch["messages"]]
    all_time = compute_message_stats(all_msgs)

    write_frequency_file(WORDS_LISTS_DIR / "all_time_frequency.txt", "ALL TIME", all_time["counter"])

    log(f"Всього повідомлень (чистих):  {all_time['n_msg']}")
    log(f"Всього слів:                  {all_time['total_words']}")
    log(f"Унікальних слів:              {all_time['unique']}")
    log(f"Словникове різноманіття:      {all_time['ttr']*100:.2f}%")
    log(f"Середня довжина повідомлення: {all_time['avg_words']:.1f} слів / {all_time['avg_chars']:.1f} символів")
    log(f"Повний словник збережено у:   {WORDS_LISTS_DIR / 'all_time_frequency.txt'}\n")

    # 4. Порівняння з розподілом частот у мові
    log("=" * 78)
    log(" 4. ПОРІВНЯННЯ З ЕТАЛОННИМ РОЗПОДІЛОМ ЧАСТОТ У МОВІ")
    log("=" * 78)
    zipf_data = compute_zipf_comparison(all_time["counter"])
    records = zipf_data["records"]
    personal = zipf_data["personal"]
    missing = zipf_data["missing_common"]
    slope = zipf_data["zipf_slope"]

    over = sorted(records, key=lambda r: r[5], reverse=True)
    log("МОЇ «ФІРМОВІ» СЛОВА — вживаю помітно частіше за норму мови:")
    log(f"{'слово':<18}{'мова':<5}{'раз':>7}{'мій Zipf':>10}{'мова Zipf':>11}{'різниця':>9}")
    log("-" * 62)
    for w, lang, c, mz, rz, d in over[:25]:
        log(f"{w:<18}{lang:<5}{c:>7}{mz:>10.2f}{rz:>11.2f}{d:>+9.2f}")

    under = sorted(records, key=lambda r: r[5])
    common_avoided = [r for r in under if r[4] >= 4.5][:25]
    log("\nЧАСТІ СЛОВА МОВИ, ЯКІ Я ВЖИВАЮ РІДШЕ ЗА ЗВИЧАЙНЕ:")
    log(f"{'слово':<18}{'мова':<5}{'раз':>7}{'мій Zipf':>10}{'мова Zipf':>11}{'різниця':>9}")
    log("-" * 62)
    for w, lang, c, mz, rz, d in common_avoided:
        log(f"{w:<18}{lang:<5}{c:>7}{mz:>10.2f}{rz:>11.2f}{d:>+9.2f}")

    if missing:
        log("\nЗ ТОП-300 НАЙЧАСТІШИХ ЛЕМ МОВИ Я МАЙЖЕ НЕ ВЖИВАЮ:")
        log("   " + ", ".join(f"{w}" + (f"({c})" if c else "") for w, c in missing[:30]))

    if personal:
        personal.sort(key=lambda r: r[2], reverse=True)
        log("\nМІЙ ОСОБИСТИЙ СЛОВНИК — часті у мене слова, яких НЕМАЄ в мовному еталоні:")
        log("   " + ", ".join(f"{w}({c})" for w, _, c, _ in personal[:40]))

    log(f"\nЗАКОН ЦІПФА: Нахил рангочастотного розподілу: {slope:.3f} (еталон ≈ -1.0)")

    # Збереження language_comparison.txt
    comp_path = WORDS_LISTS_DIR / "language_comparison.txt"
    with open(comp_path, "w", encoding="utf-8") as f:
        f.write("# ПОРІВНЯННЯ МОЄЇ ЛЕКСИКИ З ЕТАЛОННИМ РОЗПОДІЛОМ МОВИ (wordfreq)\n")
        f.write("# Формат: слово | мова | раз | мій_Zipf | еталон_Zipf | різниця\n")
        f.write("## ПЕРЕВЖИВАЮ (мої фірмові):\n")
        for w, lang, c, mz, rz, d in over:
            f.write(f"{w} | {lang} | {c} | {mz:.2f} | {rz:.2f} | {d:+.2f}\n")
        f.write("\n## НЕДОВЖИВАЮ:\n")
        for w, lang, c, mz, rz, d in under:
            f.write(f"{w} | {lang} | {c} | {mz:.2f} | {rz:.2f} | {d:+.2f}\n")
        f.write("\n## ОСОБИСТИЙ СЛОВНИК:\n")
        for w, lang, c, _mz in sorted(personal, key=lambda r: r[2], reverse=True):
            f.write(f"{w} | {lang} | {c}\n")

    # Збереження advanced_report.txt
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    saved_report_msg = f"\n[✔] Text report saved to: {REPORT_FILE}" if is_en else f"\n[✔] Текстовий звіт збережено у: {REPORT_FILE}"
    log(saved_report_msg)
    return {"status": "ok", "chats_count": len(chats), "clean_messages": filt["clean"]}


def run_full_pipeline(log_callback: Callable[[str], None] | None = None, lang: str = "uk") -> None:
    """
    Executes the complete end-to-end data analytics and visual rendering pipeline.
    """
    is_en = lang == "en"

    def log(msg: str) -> None:
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    start_time = time.time()
    header_pipeline = " STARTING FULL ANALYTICS AND INFOGRAPHICS PIPELINE" if is_en else " ПОЧАТОК ПОВНОГО ПАЙПЛАЙНУ АНАЛІТИКИ ТА ГЕНЕРАЦІЇ ІНФОГРАФІКИ"
    log("================================================================")
    log(header_pipeline)
    log("================================================================")

    # 1. Текстовий аналіз
    step1_msg = "\n[1/5] Running text analysis and frequency wordlists..." if is_en else "\n[1/5] Запуск текстового аналізу та частотних списків..."
    log(step1_msg)
    run_text_analysis(log_callback=log, lang=lang)

    chats, _ = load_chats()
    if not chats:
        no_chart_msg = "[❌] No data available for chart rendering." if is_en else "[❌] Немає даних для побудови графіків."
        log(no_chart_msg)
        return

    # 2. Базова інфографіка
    step2_msg = "\n[2/5] Generating core & basic infographics..." if is_en else "\n[2/5] Генерація базової інфографіки..."
    log(step2_msg)
    generate_basic_charts(chats)

    # 3. Поведінкова інфографіка
    step3_msg = "\n[3/5] Generating behavioral, sleep & rhythm infographics..." if is_en else "\n[3/5] Генерація інфографіки поведінки, сну та ритму..."
    log(step3_msg)
    generate_behavioral_charts(chats)

    # 4. Лінгвістична інфографіка
    step4_msg = "\n[4/5] Generating linguistic & vocabulary infographics..." if is_en else "\n[4/5] Генерація лінгвістичної інфографіки та словника..."
    log(step4_msg)
    generate_linguistic_charts(chats)

    # 5. Соціальна інфографіка
    step5_msg = "\n[5/5] Generating relationship & clustering infographics..." if is_en else "\n[5/5] Генерація інфографіки стосунків та кластеризації..."
    log(step5_msg)
    generate_social_charts(chats)

    elapsed = time.time() - start_time
    done_msg = f"\n[✔] Full pipeline successfully completed in {elapsed:.1f} sec!" if is_en else f"\n[✔] Повний пайплайн успішно завершено за {elapsed:.1f} сек!"
    log(done_msg)
