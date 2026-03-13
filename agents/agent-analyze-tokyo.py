#!/usr/bin/env python3
"""
Analiza strategii Tokyo: całe Tokyo na początku vs split (1 dzień + 2 dni na końcu)
"""

import os
import glob
import sys
import anthropic

PLAN_DIR = "/Users/bartoszrozbicki/Desktop/Claude/rozne_testy/japonia"

def read_html_plan():
    html_files = glob.glob(os.path.join(PLAN_DIR, "*.html"))
    if not html_files:
        return None
    with open(html_files[0], "r", encoding="utf-8") as f:
        return f.read()

def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Brak ANTHROPIC_API_KEY")
        sys.exit(1)

    plan_html = read_html_plan()
    if not plan_html:
        print("❌ Nie znaleziono pliku HTML")
        sys.exit(1)

    client = anthropic.Anthropic()

    print("🗼 Analiza strategii Tokyo...")
    print("=" * 60)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system="""Jesteś ekspertem od logistyki podróży po Japonii.
Analizujesz konkretny dylemat planistyczny. Odpowiadasz konkretnie, z argumentami za i przeciw,
uwzględniając zmęczenie podróżnych, jet lag, JR Pass, sezonowość i praktykę.""",
        messages=[
            {
                "role": "user",
                "content": f"""Mam plan wycieczki do Japonii (24 maja – 6 czerwca 2026, 3 osoby: dorosła para + starsza pani).

Obecny plan: 3 dni Tokyo na POCZĄTKU → dalej wycieczka po Japonii → wylot z Tokyo (bez powrotu do Tokyo).

Rozważam alternatywę: 1 dzień Tokyo na początku (po przylocie, walka z jet lagiem) → wycieczka po Japonii → 2 dni Tokyo NA KOŃCU przed wylotem.

Przeanalizuj oba warianty uwzględniając:
1. Jet lag — kiedy lepiej zwiedzać Tokyo: na świeżo czy na końcu?
2. Logistyka bagażu — czy lepiej zostawić bagaż w hotelu Tokyo na start?
3. Energia grupy — 3 dni Tokyo na początku vs rozbite
4. Atrakcje — czy 3 kolejne dni to lepszy rytm niż 1+2?
5. JR Pass i transport — czy split wpływa na strategię?
6. Specyfika grupy (starsza pani) — który wariant mniej wyczerpujący?
7. Koszty — dodatkowy nocleg w Tokyo vs oszczędność

OBECNY PLAN (skrót):
{plan_html[:3000]}...

Napisz rekomendację: który wariant lepszy i DLACZEGO. Bądź konkretny.""",
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

        final = stream.get_final_message()
        print(f"\n\n📊 Tokeny: input={final.usage.input_tokens}, output={final.usage.output_tokens}")

if __name__ == "__main__":
    main()
