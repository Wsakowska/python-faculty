"""Serwis astrologiczny — wrapper na bibliotekę kerykeion."""

import json
from kerykeion import AstrologicalSubject

# Mapowanie skrótów kerykeion na polskie nazwy znaków
SIGN_NAMES_PL = {
    "Ari": "Baran", "Tau": "Byk", "Gem": "Bliźnięta", "Can": "Rak",
    "Leo": "Lew", "Vir": "Panna", "Lib": "Waga", "Sco": "Skorpion",
    "Sag": "Strzelec", "Cap": "Koziorożec", "Aqu": "Wodnik", "Pis": "Ryby",
}

# Emoji dla znaków zodiaku
SIGN_EMOJI = {
    "Baran": "♈", "Byk": "♉", "Bliźnięta": "♊", "Rak": "♋",
    "Lew": "♌", "Panna": "♍", "Waga": "♎", "Skorpion": "♏",
    "Strzelec": "♐", "Koziorożec": "♑", "Wodnik": "♒", "Ryby": "♓",
}

# Polskie nazwy planet
PLANET_NAMES_PL = {
    "Sun": "Słońce", "Moon": "Księżyc", "Mercury": "Merkury",
    "Venus": "Wenus", "Mars": "Mars", "Jupiter": "Jowisz",
    "Saturn": "Saturn", "Uranus": "Uran", "Neptune": "Neptun",
    "Pluto": "Pluton",
}

# Polskie nazwy domów
HOUSE_NAMES_PL = {
    "First_House": "I", "Second_House": "II", "Third_House": "III",
    "Fourth_House": "IV", "Fifth_House": "V", "Sixth_House": "VI",
    "Seventh_House": "VII", "Eighth_House": "VIII", "Ninth_House": "IX",
    "Tenth_House": "X", "Eleventh_House": "XI", "Twelfth_House": "XII",
}

# Popularne polskie miasta z współrzędnymi
CITIES_PL = {
    "warszawa": (52.23, 21.01),
    "kraków": (50.06, 19.94),
    "gdańsk": (54.35, 18.65),
    "gdynia": (54.52, 18.53),
    "sopot": (54.44, 18.56),
    "wrocław": (51.11, 17.04),
    "poznań": (52.41, 16.93),
    "łódź": (51.75, 19.47),
    "szczecin": (53.43, 14.55),
    "lublin": (51.25, 22.57),
    "katowice": (50.26, 19.03),
    "białystok": (53.13, 23.16),
    "bydgoszcz": (53.12, 18.01),
    "toruń": (53.01, 18.60),
    "olsztyn": (53.78, 20.49),
    "rzeszów": (50.04, 22.00),
    "opole": (50.67, 17.93),
    "kielce": (50.87, 20.63),
    "zielona góra": (51.94, 15.51),
    "gorzów wielkopolski": (52.73, 15.24),
    "starogard gdański": (53.97, 18.53),
    "tczew": (54.09, 18.80),
    "malbork": (54.04, 19.03),
    "słupsk": (54.46, 17.03),
    "elbląg": (54.16, 19.40),
}


def get_city_coords(city_name):
    """Zwraca współrzędne (lat, lng) dla polskiego miasta.

    Args:
        city_name: Nazwa miasta (bez znaczenia wielkość liter).

    Returns:
        Tuple (lat, lng) lub None jeśli miasto nie znalezione.
    """
    return CITIES_PL.get(city_name.lower().strip())


def generate_chart(name, year, month, day, hour, minute, city, country="PL"):
    """Generuje chart urodzeniowy.

    Args:
        name: Imię osoby.
        year, month, day: Data urodzenia.
        hour, minute: Godzina urodzenia.
        city: Miasto urodzenia.
        country: Kod kraju (domyślnie PL).

    Returns:
        Dict z danymi chartu lub None przy błędzie.
    """
    coords = get_city_coords(city)
    if not coords:
        return None

    lat, lng = coords

    try:
        subject = AstrologicalSubject(
            name, year, month, day, hour, minute,
            city, country,
            lng=lng, lat=lat,
            tz_str="Europe/Warsaw",
        )
    except Exception:
        return None

    # Zbieramy pozycje planet
    planets = []
    for attr in ["sun", "moon", "mercury", "venus", "mars",
                 "jupiter", "saturn", "uranus", "neptune", "pluto"]:
        p = getattr(subject, attr)
        sign_pl = SIGN_NAMES_PL.get(p.sign, p.sign)
        planets.append({
            "name_en": p.name,
            "name_pl": PLANET_NAMES_PL.get(p.name, p.name),
            "sign": sign_pl,
            "sign_emoji": SIGN_EMOJI.get(sign_pl, ""),
            "position": round(p.position, 1),
            "house": HOUSE_NAMES_PL.get(p.house, p.house),
        })

    # Ascendent i MC
    asc_sign = SIGN_NAMES_PL.get(subject.first_house.sign, subject.first_house.sign)
    mc_sign = SIGN_NAMES_PL.get(subject.tenth_house.sign, subject.tenth_house.sign)

    chart_data = {
        "name": name,
        "sun_sign": planets[0]["sign"],
        "moon_sign": planets[1]["sign"],
        "ascendant": asc_sign,
        "mc": mc_sign,
        "planets": planets,
        "asc_position": round(subject.first_house.position, 1),
        "mc_position": round(subject.tenth_house.position, 1),
        "asc_emoji": SIGN_EMOJI.get(asc_sign, ""),
        "mc_emoji": SIGN_EMOJI.get(mc_sign, ""),
    }

    return chart_data


def chart_data_to_json(chart_data):
    """Serializuje dane chartu do JSON (do zapisu w bazie)."""
    return json.dumps(chart_data, ensure_ascii=False)


def json_to_chart_data(json_str):
    """Deserializuje dane chartu z JSON."""
    if not json_str:
        return None
    return json.loads(json_str)
