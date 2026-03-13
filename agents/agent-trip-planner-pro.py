#!/usr/bin/env python3
"""
Agent recenzji planu wycieczki do Japonii
Analizuje plan jak profesjonalny planer podróży
"""

import os
import glob
import email
import sys
from pathlib import Path
import anthropic

PLAN_DIR = "/Users/bartoszrozbicki/Desktop/Claude/rozne_testy/japonia"

def read_html_plan():
    """Szuka i odczytuje plik HTML z planem wycieczki"""
    html_files = glob.glob(os.path.join(PLAN_DIR, "*.html"))
    if not html_files:
        print("❌ Nie znaleziono pliku HTML z planem wycieczki.")
        print(f"   Szukano w: {PLAN_DIR}")
        print("   Upewnij się, że Claude skończył tworzyć plan i zapisał go jako .html")
        return None
    plan_file = html_files[0]
    print(f"✅ Znaleziono plan: {os.path.basename(plan_file)}")
    with open(plan_file, "r", encoding="utf-8") as f:
        return f.read()

def read_recommendations():
    """Odczytuje email z rekomendacjami od Doroty"""
    eml_file = os.path.join(PLAN_DIR, "Japonia - rekomendacje.eml")
    if not os.path.exists(eml_file):
        return None
    with open(eml_file, "r") as f:
        msg = email.message_from_file(f)
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            payload = part.get_payload(decode=True)
            return payload.decode("utf-8")
    return None

def review_plan(plan_html: str, recommendations: str = None) -> None:
    """Wysyła plan do Claude i strumieniuje recenzję profesjonalnego planera"""

    client = anthropic.Anthropic()

    context = f"PLAN WYCIECZKI (HTML):\n{plan_html}"
    if recommendations:
        context += f"\n\n---\nDODATKOWE REKOMENDACJE (email od znajomej):\n{recommendations}"

    print("\n🔍 Analizuję plan jako profesjonalny planer podróży...")
    print("=" * 60)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system="""Jesteś doświadczonym, profesjonalnym planerem podróży specjalizującym się w Japonii, z ponad 15-letnim doświadczeniem organizowania wycieczek premium.

Twoim zadaniem jest dogłębna recenzja planu wycieczki. Oceń go z perspektywy eksperta — krytycznie, ale konstruktywnie.

Twoja analiza musi obejmować każdy z poniższych punktów:

1. **LOGISTYKA I TRANSPORT**
   - Czy trasy między miastami są realistyczne?
   - Czy czas przejazdów jest uwzględniony?
   - JR Pass — czy jest potrzebny, na ile dni?
   - Karty IC (Suica/Pasmo) — czy wspomniane?

2. **HARMONOGRAM DZIENNY**
   - Czy plan jest przeciążony / zbyt luźny?
   - Czy czas na poszczególne atrakcje jest realistyczny?
   - Czy uwzględniono czas na dojazdy w miastach?

3. **NOCLEGI**
   - Czy każda noc jest zabezpieczona?
   - Czy lokalizacje są praktyczne (blisko atrakcji)?
   - Mix ryokan / hotel — czy odpowiedni?

4. **BUDŻET**
   - Czy budżet jest podany i realistyczny dla Japonii?
   - Szacunkowe koszty jeśli nie podano

5. **ATRAKCJE I AKTYWNOŚCI**
   - Czy lista jest kompletna dla podanych miejsc?
   - Czego brakuje — must-see, które pominięto?
   - Sezonowość — czy plan uwzględnia porę roku?

6. **REZERWACJE WYMAGAJĄCE WCZEŚNIEJSZEGO DZIAŁANIA**
   - Co trzeba zarezerwować z wyprzedzeniem?
   - Co może być trudne do zdobycia na miejscu?

7. **PRAKTYCZNE WSKAZÓWKI**
   - Wiza, ubezpieczenie, gotówka vs karta
   - Internet (e-SIM / pocket WiFi)
   - Etykieta i zwyczaje — czy wspomniane?

8. **OCENA REKOMENDACJI Z EMAILA** (jeśli dostarczone)
   - Które rekomendacje są trafione?
   - Które warto wdrożyć do planu?

9. **PODSUMOWANIE**
   - Ogólna ocena (1-10) z uzasadnieniem
   - Top 3 mocne strony planu
   - Top 3 rzeczy do poprawienia (konkretne zmiany)

Pisz po polsku. Używaj nagłówków i list punktowanych. Bądź konkretny.""",
        messages=[
            {
                "role": "user",
                "content": f"""Przeanalizuj poniższy materiał i napisz profesjonalną recenzję planu wycieczki do Japonii.

{context}""",
            }
        ],
    ) as stream:
        review_text = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            review_text += text

        final = stream.get_final_message()
        print(f"\n\n📊 Użyto tokenów: input={final.usage.input_tokens}, output={final.usage.output_tokens}")

    # Zapisz recenzję do pliku
    output_file = os.path.join(PLAN_DIR, "recenzja_planu.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Recenzja Planu Wycieczki do Japonii\n\n")
        f.write(review_text)
    print(f"\n✅ Recenzja zapisana do: recenzja_planu.md")


def main():
    print("🗾 Agent recenzji planu wycieczki do Japonii")
    print("=" * 60)

    # Sprawdź klucz API
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Brak zmiennej środowiskowej ANTHROPIC_API_KEY")
        print("   Uruchom: export ANTHROPIC_API_KEY='twój_klucz'")
        sys.exit(1)

    # Odczytaj plan HTML
    plan_html = read_html_plan()
    if not plan_html:
        sys.exit(1)

    # Odczytaj rekomendacje z emaila
    recommendations = read_recommendations()
    if recommendations:
        print("✅ Znaleziono rekomendacje od Doroty — zostaną uwzględnione w analizie")

    # Przeprowadź recenzję
    review_plan(plan_html, recommendations)


if __name__ == "__main__":
    main()
