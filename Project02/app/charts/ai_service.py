"""Serwis AI — interpretacja chartu przez Google Gemini."""

import os
from google import genai


def _get_client():
    """Zwraca klienta Gemini lub None jeśli brak klucza API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def get_ai_interpretation(chart_data):
    """Generuje interpretację chartu urodzeniowego za pomocą Gemini.

    Args:
        chart_data: Dict z danymi chartu (z astro_service.generate_chart).

    Returns:
        String z interpretacją lub None przy błędzie/braku klucza API.
    """
    client = _get_client()
    if not client:
        return None

    planets_desc = "\n".join(
        f"- {p['name_pl']}: {p['sign']} {p['position']}° (dom {p['house']})"
        for p in chart_data["planets"]
    )

    prompt = f"""Jesteś doświadczonym astrologiem. Na podstawie poniższej mapy urodzeniowej
przygotuj krótką, ale treściwą interpretację (3–5 akapitów, po polsku).

Imię: {chart_data['name']}
Słońce: {chart_data['sun_sign']}
Księżyc: {chart_data['moon_sign']}
Ascendent: {chart_data['ascendant']}
Midheaven (MC): {chart_data['mc']}

Pozycje planet:
{planets_desc}

Opisz:
1. Ogólny charakter osobowości (Słońce + Ascendent)
2. Świat emocji i potrzeby wewnętrzne (Księżyc)
3. Komunikację i styl myślenia (Merkury)
4. Miłość i relacje (Wenus + Mars)
5. Główne wyzwania i potencjał rozwoju

Pisz przystępnym językiem, unikaj żargonu astrologicznego bez wyjaśnienia.
Odpowiedź sformatuj w HTML (użyj tagów <h5>, <p>, <strong>)."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None


def get_synastry_interpretation(chart1, chart2):
    """Generuje interpretację synastrii za pomocą Gemini.

    Args:
        chart1, chart2: Dicts z danymi chartów.

    Returns:
        String z interpretacją lub None przy błędzie.
    """
    client = _get_client()
    if not client:
        return None

    prompt = f"""Jesteś doświadczonym astrologiem. Porównaj dwie mapy urodzeniowe
i przygotuj analizę synastrii (3–5 akapitów, po polsku).

OSOBA 1 — {chart1['name']}:
Słońce: {chart1['sun_sign']}, Księżyc: {chart1['moon_sign']}, Ascendent: {chart1['ascendant']}

OSOBA 2 — {chart2['name']}:
Słońce: {chart2['sun_sign']}, Księżyc: {chart2['moon_sign']}, Ascendent: {chart2['ascendant']}

Opisz:
1. Ogólna kompatybilność (żywioły, modalności)
2. Komunikacja i zrozumienie
3. Emocjonalne połączenie (Księżyce)
4. Romantyczna chemia (Wenus i Mars)
5. Potencjalne tarcia i jak je rozwiązywać

Pisz przystępnym językiem. Odpowiedź sformatuj w HTML (użyj tagów <h5>, <p>, <strong>)."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None