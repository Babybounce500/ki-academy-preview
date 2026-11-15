"""vibe - die Vibe-Coding-Bibliothek: nuetzliche, beeindruckende Funktionen in reinem Python.

Nur Standardbibliothek, laeuft in der Python-IDE (Pyodide) und in jedem normalen Python 3.9+.

    from vibe import *          # alles
    import vibe; vibe.hilfe()    # Uebersicht mit Beispielen

Kategorien: Text, Zahlen und Finanzen, Datum (Deutschland), Daten und Analyse,
Algorithmen und Puzzle, Werkzeuge, Web und KI.
"""
import asyncio
import collections
import datetime as _dt
import difflib
import functools
import heapq
import html as _html
import itertools
import json
import math
import random
import re
import secrets
import statistics as _st
import string
import time
import unicodedata

__version__ = "1.0.0"

_KATALOG = []


def _reg(kategorie, beschreibung, beispiel):
    """Traegt eine Funktion/Klasse mit Beschreibung und Beispielcode in den Katalog ein."""
    def deko(obj):
        _KATALOG.append({"name": obj.__name__, "kategorie": kategorie, "beschreibung": beschreibung, "beispiel": beispiel})
        return obj
    return deko


# =============================================================================
# TEXT
# =============================================================================
_UMLAUTE = {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"}


@_reg("Text", "URL-taugliche Kurzform mit deutschen Umlauten", 'print(slugify("Große Straße 12: Ärger über Öl!"))')
def slugify(text, trenner="-"):
    for k, v in _UMLAUTE.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", trenner, text).strip(trenner).lower()


_E = ["null", "ein", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf",
      "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"]
_Z = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]


def _unter100(n, ende):
    if n < 20:
        return "eins" if (n == 1 and ende) else _E[n]
    z, e = divmod(n, 10)
    if e == 0:
        return _Z[z]
    return ("ein" if e == 1 else _E[e]) + "und" + _Z[z]


def _unter1000(n, ende):
    h, r = divmod(n, 100)
    s = ""
    if h:
        s += ("ein" if h == 1 else _E[h]) + "hundert"
    if r:
        s += _unter100(r, ende)
    return s


@_reg("Text", "Zahl in deutsche Worte (bis 999 Milliarden)", 'for n in (0, 21, 101, 1000, 1234567, 2000001, -15):\n    print(n, "=", zahl_zu_wort(n))')
def zahl_zu_wort(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("zahl_zu_wort erwartet eine ganze Zahl")
    if n < 0:
        return "minus " + zahl_zu_wort(-n)
    if n == 0:
        return "null"
    if n >= 10 ** 12:
        raise ValueError("Zahl zu gross (maximal 999 Milliarden)")
    teile = []
    mrd, rest = divmod(n, 10 ** 9)
    mio, rest = divmod(rest, 10 ** 6)
    if mrd:
        teile.append("eine Milliarde" if mrd == 1 else zahl_zu_wort(mrd) + " Milliarden")
    if mio:
        teile.append("eine Million" if mio == 1 else zahl_zu_wort(mio) + " Millionen")
    if rest:
        tsd, r = divmod(rest, 1000)
        s = ""
        if tsd:
            s += ("ein" if tsd == 1 else _unter1000(tsd, False)) + "tausend"
        if r:
            s += _unter1000(r, True)
        teile.append(s)
    return " ".join(teile)


_R = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
      (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


@_reg("Text", "Roemische Zahlen: Zahl zu Roemisch", 'print(roemisch(1994), roemisch(2024), roemisch(3999))')
def roemisch(n):
    if not 0 < n < 4000:
        raise ValueError("Roemische Zahlen gibt es hier von 1 bis 3999")
    s = ""
    for wert, zeichen in _R:
        while n >= wert:
            s += zeichen
            n -= wert
    return s


@_reg("Text", "Roemische Zahlen: Roemisch zu Zahl (mit Pruefung)", 'print(aus_roemisch("MCMXCIV"))')
def aus_roemisch(text):
    t = text.upper()
    werte = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    if not t or any(c not in werte for c in t):
        raise ValueError("Ungueltige roemische Zahl: " + text)
    summe = 0
    for i, c in enumerate(t):
        w = werte[c]
        summe += -w if i + 1 < len(t) and werte[t[i + 1]] > w else w
    if roemisch(summe) != t:
        raise ValueError("Ungueltige roemische Zahl: " + text)
    return summe


_STOP = set("der die das und oder aber ein eine einen einem einer eines ist sind war waren wird werden wurde wurden zu zum zur von "
            "vom mit auf in im an am aus bei nach für über unter dass den dem des es sie er wir ihr ich du nicht auch als wie so noch "
            "nur sich sein seine ihre ihren hat haben dann wenn".split())


@_reg("Text", "Haeufigste Woerter (ohne deutsche Fuellwoerter)", 'text = "Python ist toll. Python macht Spass und Python ist einfach."\nprint(woerter_zaehlen(text, top=3))')
def woerter_zaehlen(text, top=10, stopwoerter=True):
    w = re.findall(r"[A-Za-zÄÖÜäöüß]+", text.lower())
    if stopwoerter:
        w = [x for x in w if x not in _STOP and len(x) > 2]
    return collections.Counter(w).most_common(top)


@_reg("Text", "Extraktive Zusammenfassung: die wichtigsten Saetze", 'text = "Katzen schlafen viel. Katzen jagen Maeuse. Der Himmel ist blau. Katzen sind Raubtiere."\nprint(zusammenfassung(text, saetze=2))')
def zusammenfassung(text, saetze=2):
    teile = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if len(teile) <= saetze:
        return " ".join(teile)
    haeufig = dict(woerter_zaehlen(text, top=10 ** 6))
    punkte = []
    for i, s in enumerate(teile):
        w = [x for x in re.findall(r"[A-Za-zÄÖÜäöüß]+", s.lower()) if x not in _STOP and len(x) > 2]
        punkte.append((sum(haeufig.get(x, 0) for x in w) / (len(w) or 1), -i, i))
    beste = sorted(punkte, reverse=True)[:saetze]
    return " ".join(teile[i] for i in sorted(p[2] for p in beste))


@_reg("Text", "Editierabstand zweier Woerter (Levenshtein)", 'print(levenshtein("kitten", "sitting"), levenshtein("Sonntag", "Samstag"))')
def levenshtein(a, b):
    vor = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        akt = [i]
        for j, cb in enumerate(b, 1):
            akt.append(min(vor[j] + 1, akt[j - 1] + 1, vor[j - 1] + (ca != cb)))
        vor = akt
    return vor[-1]


@_reg("Text", "Aehnlichkeit zweier Texte von 0 bis 1", 'print(aehnlichkeit("Python lernen", "Python lernen!"))')
def aehnlichkeit(a, b):
    return round(difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio(), 3)


@_reg("Text", "Fehlertolerante Suche in einer Liste", 'print(fuzzy_suche("pythn", ["Python", "Pizza", "Pyramide", "Java"], n=2))')
def fuzzy_suche(anfrage, liste, n=3):
    bewertet = sorted(((aehnlichkeit(anfrage, x), x) for x in liste), key=lambda t: (-t[0], t[1]))
    return [x for _, x in bewertet[:n]]


@_reg("Text", "Caesar-Verschluesselung", 'geheim = caesar("Hallo Welt", 3)\nprint(geheim, caesar(geheim, -3))')
def caesar(text, verschiebung):
    def tausch(c):
        if "a" <= c <= "z":
            return chr((ord(c) - 97 + verschiebung) % 26 + 97)
        if "A" <= c <= "Z":
            return chr((ord(c) - 65 + verschiebung) % 26 + 65)
        return c
    return "".join(tausch(c) for c in text)


@_reg("Text", "Vigenere-Verschluesselung mit Schluesselwort", 'g = vigenere("Angriff im Morgengrauen", "KEY")\nprint(g, vigenere(g, "KEY", entschluesseln=True))')
def vigenere(text, schluessel, entschluesseln=False):
    s = [ord(c.lower()) - 97 for c in schluessel if c.isalpha()]
    if not s:
        raise ValueError("Schluesselwort braucht Buchstaben")
    aus, i = [], 0
    for c in text:
        if c.isascii() and c.isalpha():
            k = s[i % len(s)] * (-1 if entschluesseln else 1)
            basis = 65 if c.isupper() else 97
            aus.append(chr((ord(c) - basis + k) % 26 + basis))
            i += 1
        else:
            aus.append(c)
    return "".join(aus)


@_reg("Text", "Palindrom-Test (ignoriert Satzzeichen)", 'print(ist_palindrom("Ein Neger mit Gazelle zagt im Regen nie"))')
def ist_palindrom(text):
    t = "".join(c.lower() for c in text if c.isalnum())
    return t == t[::-1] and bool(t)


@_reg("Text", "Geschaetzte Lesezeit", 'print(lesezeit("wort " * 450))')
def lesezeit(text, woerter_pro_minute=200):
    n = len(re.findall(r"\w+", text))
    return {"woerter": n, "minuten": round(n / woerter_pro_minute, 1)}


@_reg("Text", "Mini-Markdown zu sicherem HTML", 'print(markdown_zu_html("# Titel\\n\\nEin **fetter** Text mit `code` und [Link](https://example.org).\\n\\n- eins\\n- zwei"))')
def markdown_zu_html(md):
    def inline(t):
        t = _html.escape(t, quote=False)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
        t = re.sub(r"\[([^\]]+)\]\(((?:https?://|/|\./|#)[^)\s]*)\)", r'<a href="\2">\1</a>', t)
        return t
    aus, liste, absatz, code = [], None, [], None

    def liste_zu():
        nonlocal liste
        if liste:
            aus.append("</" + liste + ">")
            liste = None

    def absatz_zu():
        nonlocal absatz
        if absatz:
            aus.append("<p>" + inline(" ".join(absatz)) + "</p>")
            absatz = []
    for zeile in md.split("\n"):
        if zeile.strip().startswith("```"):
            if code is None:
                absatz_zu(); liste_zu(); code = []
            else:
                aus.append("<pre><code>" + _html.escape("\n".join(code)) + "</code></pre>")
                code = None
            continue
        if code is not None:
            code.append(zeile)
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", zeile)
        li = re.match(r"^\s*[-*]\s+(.*)$", zeile)
        nu = re.match(r"^\s*\d+[.)]\s+(.*)$", zeile)
        if m:
            absatz_zu(); liste_zu()
            aus.append("<h%d>%s</h%d>" % (len(m[1]), inline(m[2]), len(m[1])))
        elif li or nu:
            absatz_zu()
            art = "ul" if li else "ol"
            if liste != art:
                liste_zu(); aus.append("<" + art + ">"); liste = art
            aus.append("<li>" + inline((li or nu)[1]) + "</li>")
        elif not zeile.strip():
            absatz_zu(); liste_zu()
        else:
            liste_zu(); absatz.append(zeile.strip())
    if code is not None:
        aus.append("<pre><code>" + _html.escape("\n".join(code)) + "</code></pre>")
    absatz_zu(); liste_zu()
    return "\n".join(aus)


_FILTER = {
    "upper": lambda v: str(v).upper(), "lower": lambda v: str(v).lower(), "title": lambda v: str(v).title(),
    "strip": lambda v: str(v).strip(), "len": len, "int": int,
    "round1": lambda v: round(float(v), 1), "round2": lambda v: round(float(v), 2),
    "euro": lambda v: ("{:,.2f}".format(float(v)).replace(",", "X").replace(".", ",").replace("X", ".")) + " €",
    "datum": lambda v: v.strftime("%d.%m.%Y"),
}


@_reg("Text", "Kleine Vorlagen-Engine mit Filtern", 'print(vorlage("Hallo {{ name|title }}, du schuldest {{ betrag|euro }} bis {{ tag|datum }}.", name="anna lang", betrag=1234.5, tag=__import__("datetime").date(2025, 3, 1)))')
def vorlage(text, **werte):
    def ersetze(m):
        teile = [t.strip() for t in m.group(1).split("|")]
        name = teile[0]
        if name not in werte:
            raise KeyError("Variable fehlt in der Vorlage: " + name)
        v = werte[name]
        for f in teile[1:]:
            if f not in _FILTER:
                raise ValueError("Unbekannter Filter: " + f)
            v = _FILTER[f](v)
        return str(v)
    return re.sub(r"\{\{\s*([^{}]+?)\s*\}\}", ersetze, text)


# =============================================================================
# ZAHLEN UND FINANZEN
# =============================================================================
@_reg("Zahlen und Finanzen", "Luhn-Pruefung (Kreditkarten, IMEI)", 'print(luhn_ok("4539 1488 0343 6467"), luhn_ok("4539 1488 0343 6468"))')
def luhn_ok(nummer):
    z = [int(c) for c in str(nummer) if c.isdigit()]
    if len(z) < 2:
        return False
    summe = 0
    for i, d in enumerate(reversed(z)):
        if i % 2:
            d *= 2
            if d > 9:
                d -= 9
        summe += d
    return summe % 10 == 0


@_reg("Zahlen und Finanzen", "IBAN-Pruefung (Pruefsumme Modulo 97)", 'print(iban_ok("DE89 3704 0044 0532 0130 00"), iban_ok("DE89 3704 0044 0532 0130 01"))')
def iban_ok(iban):
    s = re.sub(r"\s+", "", iban).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", s):
        return False
    s = s[4:] + s[:4]
    zahl = "".join(str(int(c, 36)) for c in s)
    return int(zahl) % 97 == 1


@_reg("Zahlen und Finanzen", "Monatliche Kreditrate (Annuitaet)", 'print(rate_annuitaet(250000, 3.6, 20))')
def rate_annuitaet(kredit, zins_pa, jahre):
    n = jahre * 12
    i = zins_pa / 100 / 12
    if i == 0:
        return round(kredit / n, 2)
    return round(kredit * i / (1 - (1 + i) ** -n), 2)


@_reg("Zahlen und Finanzen", "Tilgungsplan Monat fuer Monat", 'plan = tilgungsplan(10000, 5, 1)\nprint(tabelle([[p["monat"], p["rate"], p["zins"], p["tilgung"], p["restschuld"]] for p in plan[:3]], ["Monat", "Rate", "Zins", "Tilgung", "Rest"]))')
def tilgungsplan(kredit, zins_pa, jahre):
    n = jahre * 12
    i = zins_pa / 100 / 12
    rate = rate_annuitaet(kredit, zins_pa, jahre)
    rest, plan = float(kredit), []
    for m in range(1, n + 1):
        zins = round(rest * i, 2)
        tilg = round(rate - zins, 2)
        if m == n:
            tilg = round(rest, 2)
            r = round(zins + tilg, 2)
        else:
            r = rate
        rest = round(rest - tilg, 2)
        plan.append({"monat": m, "rate": r, "zins": zins, "tilgung": tilg, "restschuld": max(rest, 0.0)})
    return plan


@_reg("Zahlen und Finanzen", "Zinseszins mit jaehrlicher Sparrate", 'print(zinseszins(1000, 5, 10), zinseszins(0, 4, 30, sparrate_jahr=1200))')
def zinseszins(kapital, zins_pa, jahre, sparrate_jahr=0):
    z = zins_pa / 100
    if z == 0:
        return round(kapital + sparrate_jahr * jahre, 2)
    return round(kapital * (1 + z) ** jahre + sparrate_jahr * ((1 + z) ** jahre - 1) / z, 2)


@_reg("Zahlen und Finanzen", "Mehrwertsteuer berechnen (netto zu brutto)", 'print(mwst(100), mwst(100, 7))')
def mwst(netto, satz=19):
    steuer = round(netto * satz / 100, 2)
    return {"netto": round(netto, 2), "mwst": steuer, "brutto": round(netto + steuer, 2)}


@_reg("Zahlen und Finanzen", "Netto aus Bruttobetrag herausrechnen", 'print(netto_aus_brutto(119))')
def netto_aus_brutto(brutto, satz=19):
    netto = round(brutto / (1 + satz / 100), 2)
    return {"netto": netto, "mwst": round(brutto - netto, 2), "brutto": round(brutto, 2)}


@_reg("Zahlen und Finanzen", "Alle Primzahlen bis n (Sieb)", 'print(primzahlen(50), len(primzahlen(100000)))')
def primzahlen(bis):
    if bis < 2:
        return []
    s = bytearray([1]) * (bis + 1)
    s[0] = s[1] = 0
    for i in range(2, int(bis ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(range(i * i, bis + 1, i)))
    return [i for i, v in enumerate(s) if v]


@_reg("Zahlen und Finanzen", "Primfaktorzerlegung", 'print(primfaktoren(360), primfaktoren(600851475143))')
def primfaktoren(n):
    if n < 2:
        return []
    f, d = [], 2
    while d * d <= n:
        while n % d == 0:
            f.append(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f.append(n)
    return f


@_reg("Zahlen und Finanzen", "Collatz-Folge: Schritte und Maximum", 'print(collatz(27))')
def collatz(n):
    schritte, maximum = 0, n
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        maximum = max(maximum, n)
        schritte += 1
    return schritte, maximum


_ZIFFERN = "0123456789abcdefghijklmnopqrstuvwxyz"


@_reg("Zahlen und Finanzen", "Zahlensysteme umrechnen (2 bis 36)", 'print(basis_umrechnen(255, 10, 2), basis_umrechnen("ff", 16, 10), basis_umrechnen(123456789, 10, 36))')
def basis_umrechnen(zahl, von=10, nach=2):
    n = int(str(zahl), von)
    if n == 0:
        return "0"
    vorz, n, s = ("-" if n < 0 else ""), abs(n), ""
    while n:
        n, r = divmod(n, nach)
        s = _ZIFFERN[r] + s
    return vorz + s


_EINHEITEN = {
    "laenge": {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "zoll": 0.0254, "fuss": 0.3048, "meile": 1609.344, "yard": 0.9144},
    "gewicht": {"g": 1, "kg": 1000, "t": 1e6, "pfund": 453.59237, "unze": 28.349523125},
    "volumen": {"l": 1, "ml": 0.001, "m3": 1000, "gallone": 3.785411784},
    "tempo": {"m/s": 1, "km/h": 1 / 3.6, "mph": 0.44704, "knoten": 1852 / 3600},
}


@_reg("Zahlen und Finanzen", "Einheiten umrechnen (Laenge, Gewicht, Volumen, Tempo, Temperatur)", 'print(einheit(1, "meile", "km"), einheit(100, "c", "f"), einheit(5, "pfund", "kg"))')
def einheit(wert, von, nach):
    t = {"c", "f", "k"}
    if von in t and nach in t:
        c = wert if von == "c" else (wert - 32) * 5 / 9 if von == "f" else wert - 273.15
        return round(c if nach == "c" else c * 9 / 5 + 32 if nach == "f" else c + 273.15, 6)
    for tabelle_ in _EINHEITEN.values():
        if von in tabelle_ and nach in tabelle_:
            return round(wert * tabelle_[von] / tabelle_[nach], 9)
    raise ValueError("Einheiten passen nicht zusammen: %s -> %s" % (von, nach))


@_reg("Zahlen und Finanzen", "Body-Mass-Index mit Einordnung", 'print(bmi(70, 175))')
def bmi(kg, cm):
    w = round(kg / (cm / 100) ** 2, 2)
    k = "Untergewicht" if w < 18.5 else "Normalgewicht" if w < 25 else "Uebergewicht" if w < 30 else "Adipositas"
    return w, k


# =============================================================================
# DATUM (DEUTSCHLAND)
# =============================================================================
_TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
_MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
BUNDESLAENDER = ["BW", "BY", "BE", "BB", "HB", "HH", "HE", "MV", "NI", "NW", "RP", "SL", "SN", "ST", "SH", "TH"]


@_reg("Datum (Deutschland)", "Ostersonntag eines Jahres (Gauss/Meeus)", 'print(ostern(2024), ostern(2025), ostern(2038))')
def ostern(jahr):
    a, b, c = jahr % 19, jahr // 100, jahr % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    monat = (h + l - 7 * m + 114) // 31
    tag = (h + l - 7 * m + 114) % 31 + 1
    return _dt.date(jahr, monat, tag)


@_reg("Datum (Deutschland)", "Gesetzliche Feiertage nach Bundesland (Kuerzel wie NW, BY, BE)", 'for tag, name in feiertage(2025, "BY").items():\n    print(tag.strftime("%d.%m.%Y"), wochentag(tag)[:2], name)')
def feiertage(jahr, land="NW"):
    land = land.upper()
    if land not in BUNDESLAENDER:
        raise ValueError("Unbekanntes Bundesland: %s (erlaubt: %s)" % (land, ", ".join(BUNDESLAENDER)))
    o = ostern(jahr)
    d = _dt.timedelta
    f = {_dt.date(jahr, 1, 1): "Neujahr", o - d(days=2): "Karfreitag", o + d(days=1): "Ostermontag",
         _dt.date(jahr, 5, 1): "Tag der Arbeit", o + d(days=39): "Christi Himmelfahrt", o + d(days=50): "Pfingstmontag",
         _dt.date(jahr, 10, 3): "Tag der Deutschen Einheit", _dt.date(jahr, 12, 25): "1. Weihnachtstag",
         _dt.date(jahr, 12, 26): "2. Weihnachtstag"}
    if land in ("BW", "BY", "ST"):
        f[_dt.date(jahr, 1, 6)] = "Heilige Drei Könige"
    if land in ("BE", "MV") and jahr >= (2019 if land == "BE" else 2023):
        f[_dt.date(jahr, 3, 8)] = "Internationaler Frauentag"
    if land in ("BW", "BY", "HE", "NW", "RP", "SL"):
        f[o + d(days=60)] = "Fronleichnam"
    if land == "SL":
        f[_dt.date(jahr, 8, 15)] = "Mariä Himmelfahrt"
    if land == "TH" and jahr >= 2019:
        f[_dt.date(jahr, 9, 20)] = "Weltkindertag"
    if land in ("BB", "MV", "SN", "ST", "TH") or (land in ("HB", "HH", "NI", "SH") and jahr >= 2018):
        f[_dt.date(jahr, 10, 31)] = "Reformationstag"
    if land in ("BW", "BY", "NW", "RP", "SL"):
        f[_dt.date(jahr, 11, 1)] = "Allerheiligen"
    if land == "SN":
        b = _dt.date(jahr, 11, 22)
        while b.weekday() != 2:
            b -= d(days=1)
        f[b] = "Buß- und Bettag"
    return dict(sorted(f.items()))


@_reg("Datum (Deutschland)", "Werktage zwischen zwei Daten (ohne Wochenende und Feiertage)", 'import datetime as dt\nprint(werktage(dt.date(2024, 12, 23), dt.date(2024, 12, 31), "NW"))')
def werktage(von, bis, land="NW"):
    n, tag = 0, von
    feste = {}
    while tag <= bis:
        if tag.year not in feste:
            feste[tag.year] = feiertage(tag.year, land)
        if tag.weekday() < 5 and tag not in feste[tag.year]:
            n += 1
        tag += _dt.timedelta(days=1)
    return n


@_reg("Datum (Deutschland)", "n Werktage zu einem Datum addieren", 'import datetime as dt\nprint(addiere_werktage(dt.date(2024, 12, 20), 5, "NW"))')
def addiere_werktage(start, n, land="NW"):
    tag, rest, feste = start, n, {}
    while rest > 0:
        tag += _dt.timedelta(days=1)
        if tag.year not in feste:
            feste[tag.year] = feiertage(tag.year, land)
        if tag.weekday() < 5 and tag not in feste[tag.year]:
            rest -= 1
    return tag


@_reg("Datum (Deutschland)", "Alter in Jahren, Monaten und Tagen", 'import datetime as dt\nprint(alter(dt.date(1990, 5, 17), dt.date(2025, 3, 1)))')
def alter(geburtstag, am=None):
    am = am or _dt.date.today()
    j, m, t = am.year - geburtstag.year, am.month - geburtstag.month, am.day - geburtstag.day
    if t < 0:
        m -= 1
        vormonat = (am.replace(day=1) - _dt.timedelta(days=1))
        t += vormonat.day
    if m < 0:
        j -= 1
        m += 12
    return j, m, t


@_reg("Datum (Deutschland)", "Deutscher Wochentagsname", 'import datetime as dt\nprint(wochentag(dt.date(2024, 5, 17)))')
def wochentag(datum):
    return _TAGE[datum.weekday()]


@_reg("Datum (Deutschland)", "ISO-Kalenderwoche", 'import datetime as dt\nprint(kalenderwoche(dt.date(2024, 12, 30)))')
def kalenderwoche(datum):
    return datum.isocalendar()[1]


@_reg("Datum (Deutschland)", "Datum aus deutschem Text lesen (17.05.2024, 17. Mai 2024, 2024-05-17)", 'print(datum_parsen("17. Mai 2024"), datum_parsen("1.3.25"))')
def datum_parsen(text):
    t = text.strip()
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})", t)
    if m:
        j = int(m[3]) + (2000 if len(m[3]) == 2 else 0)
        return _dt.date(j, int(m[2]), int(m[1]))
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        return _dt.date(int(m[1]), int(m[2]), int(m[3]))
    m = re.fullmatch(r"(\d{1,2})\.?\s+([A-Za-zä]+)\s+(\d{4})", t)
    if m and m[2].capitalize() in _MONATE:
        return _dt.date(int(m[3]), _MONATE.index(m[2].capitalize()) + 1, int(m[1]))
    raise ValueError("Datum nicht erkannt: " + text)


# =============================================================================
# DATEN UND ANALYSE
# =============================================================================
@_reg("Daten und Analyse", "Huebsche Tabelle als Text (Unicode-Rahmen)", 'print(tabelle([["Anna", 31, 4200.5], ["Ben", 27, 3900]], ["Name", "Alter", "Gehalt"]))')
def tabelle(zeilen, kopf=None):
    z = [[("" if c is None else str(c)) for c in r] for r in zeilen]
    k = [str(c) for c in kopf] if kopf else None
    spalten = max(len(r) for r in (z + ([k] if k else [])))
    alle = ([k] if k else []) + z
    breiten = [max((len(r[i]) if i < len(r) else 0) for r in alle) for i in range(spalten)]
    zahl = [all(re.fullmatch(r"-?[\d.,]+", r[i]) for r in z if i < len(r) and r[i]) for i in range(spalten)]

    def zeile(r, kopfzeile=False):
        zellen = []
        for i in range(spalten):
            t = r[i] if i < len(r) else ""
            zellen.append(t.rjust(breiten[i]) if zahl[i] and not kopfzeile else t.ljust(breiten[i]))
        return "│ " + " │ ".join(zellen) + " │"
    def linie(l, m, r):
        return l + m.join("─" * (b + 2) for b in breiten) + r
    aus = [linie("┌", "┬", "┐")]
    if k:
        aus += [zeile(k, True), linie("├", "┼", "┤")]
    aus += [zeile(r) for r in z]
    aus.append(linie("└", "┴", "┘"))
    return "\n".join(aus)


@_reg("Daten und Analyse", "Balkendiagramm aus Text", 'print(balken({"Python": 48, "JavaScript": 40, "Rust": 12}))')
def balken(daten, breite=30):
    paare = list(daten.items()) if isinstance(daten, dict) else list(daten)
    if not paare:
        return ""
    m = max(abs(v) for _, v in paare) or 1
    nl = max(len(str(k)) for k, _ in paare)
    return "\n".join("%s │%s %s" % (str(k).ljust(nl), "█" * round(abs(v) / m * breite), v) for k, v in paare)


@_reg("Daten und Analyse", "Sparkline: Verlauf in einer Textzeile", 'print(sparkline([1, 3, 2, 8, 5, 9, 4, 6]))')
def sparkline(werte):
    zeichen = "▁▂▃▄▅▆▇█"
    lo, hi = min(werte), max(werte)
    if hi == lo:
        return zeichen[0] * len(werte)
    return "".join(zeichen[min(7, int((v - lo) / (hi - lo) * 8))] for v in werte)


@_reg("Daten und Analyse", "Histogramm als Text", 'import random\nrandom.seed(3)\nprint(histogramm_text([random.gauss(50, 10) for _ in range(400)], klassen=8))')
def histogramm_text(werte, klassen=8, breite=30):
    lo, hi = min(werte), max(werte)
    schritt = (hi - lo) / klassen or 1
    zaehler = [0] * klassen
    for v in werte:
        zaehler[min(klassen - 1, int((v - lo) / schritt))] += 1
    m = max(zaehler) or 1
    return "\n".join("%8.1f │%s %d" % (lo + i * schritt, "█" * round(c / m * breite), c) for i, c in enumerate(zaehler))


@_reg("Daten und Analyse", "Statistik-Zusammenfassung einer Zahlenliste", 'print(statistik([2, 4, 4, 4, 5, 5, 7, 9]))')
def statistik(werte):
    w = sorted(werte)
    n = len(w)
    q = _st.quantiles(w, n=4, method="inclusive") if n >= 2 else [w[0]] * 3
    try:
        modus = _st.mode(w)
    except _st.StatisticsError:
        modus = None
    return {"anzahl": n, "summe": sum(w), "mittel": round(_st.mean(w), 4), "median": _st.median(w),
            "std": round(_st.stdev(w), 4) if n > 1 else 0.0, "min": w[0], "max": w[-1], "q1": q[0], "q3": q[2], "modus": modus}


@_reg("Daten und Analyse", "Korrelation nach Pearson", 'print(korrelation([1, 2, 3, 4], [2, 4, 6, 8.5]))')
def korrelation(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        raise ValueError("Keine Streuung: Korrelation nicht definiert")
    return round(sxy / math.sqrt(sxx * syy), 6)


@_reg("Daten und Analyse", "Lineare Regression: Steigung, Achsenabschnitt, R-Quadrat", 'print(lineare_regression([1, 2, 3, 4, 5], [3, 5, 7, 9, 11]))')
def lineare_regression(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        raise ValueError("Alle x-Werte sind gleich")
    m = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    c = my - m * mx
    ss_tot = sum((b - my) ** 2 for b in y)
    ss_res = sum((b - (m * a + c)) ** 2 for a, b in zip(x, y))
    return round(m, 10), round(c, 10), (1.0 if ss_tot == 0 else round(1 - ss_res / ss_tot, 10))


@_reg("Daten und Analyse", "k-Means-Clustering (k-means++, reproduzierbar)", 'punkte = [(1, 1), (1.5, 2), (1, 0.5), (8, 8), (9, 9), (8.5, 7.5)]\nzentren, labels = kmeans(punkte, k=2, seed=1)\nprint(sorted(labels), [tuple(round(c, 2) for c in z) for z in sorted(zentren)])')
def kmeans(punkte, k=2, seed=0, iterationen=100):
    rnd = random.Random(seed)
    pts = [tuple(float(c) for c in p) for p in punkte]
    if k > len(pts):
        raise ValueError("k ist groesser als die Zahl der Punkte")
    def d2(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b))
    zentren = [rnd.choice(pts)]
    while len(zentren) < k:
        abst = [min(d2(p, c) for c in zentren) for p in pts]
        gesamt = sum(abst)
        if gesamt == 0:
            zentren.append(rnd.choice(pts))
            continue
        r, acc = rnd.random() * gesamt, 0
        for p, a in zip(pts, abst):
            acc += a
            if acc >= r:
                zentren.append(p)
                break
    labels = [0] * len(pts)
    for _ in range(iterationen):
        neu = [min(range(k), key=lambda j: d2(p, zentren[j])) for p in pts]
        if neu == labels and _ > 0:
            break
        labels = neu
        for j in range(k):
            mitglieder = [p for p, l in zip(pts, labels) if l == j]
            if mitglieder:
                zentren[j] = tuple(sum(c) / len(mitglieder) for c in zip(*mitglieder))
    return zentren, labels


@_reg("Daten und Analyse", "Gleitender Mittelwert", 'print(gleitender_mittelwert([1, 2, 3, 4, 5, 6], 3))')
def gleitender_mittelwert(werte, fenster=3):
    return [round(sum(werte[i:i + fenster]) / fenster, 6) for i in range(len(werte) - fenster + 1)]


@_reg("Daten und Analyse", "Werte auf 0 bis 1 skalieren", 'print(normalisieren([10, 20, 15, 30]))')
def normalisieren(werte):
    lo, hi = min(werte), max(werte)
    return [0.0 if hi == lo else round((v - lo) / (hi - lo), 6) for v in werte]


@_reg("Daten und Analyse", "CSV-Text in Liste von Dicts (erkennt ; und , und Zahlen)", 'print(csv_zu_dicts("name;alter;ort\\nAnna;31;Köln\\nBen;27;Bonn"))')
def csv_zu_dicts(text, trenner=None):
    import csv
    import io
    zeilen = text.strip().splitlines()
    if trenner is None:
        trenner = ";" if zeilen and zeilen[0].count(";") >= zeilen[0].count(",") and ";" in zeilen[0] else ","
    def zahl(v):
        for typ in (int, float):
            try:
                return typ(v)
            except ValueError:
                pass
        return v
    return [{k: zahl(v) for k, v in r.items()} for r in csv.DictReader(io.StringIO("\n".join(zeilen)), delimiter=trenner)]


@_reg("Daten und Analyse", "Zeilen gruppieren und aggregieren (wie GROUP BY)", 'zeilen = [{"stadt": "Koeln", "umsatz": 10}, {"stadt": "Bonn", "umsatz": 5}, {"stadt": "Koeln", "umsatz": 7}]\nprint(gruppieren(zeilen, "stadt", lambda r: sum(x["umsatz"] for x in r)))')
def gruppieren(zeilen, schluessel, aggregat=None):
    g = collections.defaultdict(list)
    for z in zeilen:
        g[z[schluessel] if isinstance(schluessel, str) else schluessel(z)].append(z)
    return {k: (aggregat(v) if aggregat else v) for k, v in g.items()}


@_reg("Daten und Analyse", "Pi per Monte-Carlo-Simulation schaetzen", 'print(monte_carlo_pi(200000, seed=1))')
def monte_carlo_pi(n=100000, seed=None):
    r = random.Random(seed)
    innen = sum(1 for _ in range(n) if r.random() ** 2 + r.random() ** 2 <= 1)
    return 4 * innen / n


# =============================================================================
# ALGORITHMEN UND PUZZLE
# =============================================================================
@_reg("Algorithmen und Puzzle", "Sudoku loesen (81 Zeichen, 0 oder . fuer leer)", 'puzzle = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"\nloesung = sudoku_loesen(puzzle)\nfor i in range(0, 81, 9):\n    print(loesung[i:i + 9])')
def sudoku_loesen(raster):
    s = [0 if c in ".0" else int(c) for c in raster.replace("\n", "").replace(" ", "")]
    if len(s) != 81:
        raise ValueError("Ein Sudoku braucht genau 81 Zeichen")
    z, sp, bl = [0] * 9, [0] * 9, [0] * 9
    for i, v in enumerate(s):
        if v:
            bit = 1 << v
            r, c = divmod(i, 9)
            b = r // 3 * 3 + c // 3
            if z[r] & bit or sp[c] & bit or bl[b] & bit:
                return None
            z[r] |= bit; sp[c] |= bit; bl[b] |= bit

    def loese():
        beste, mgl = None, 10
        for i in range(81):
            if s[i] == 0:
                r, c = divmod(i, 9)
                frei = [v for v in range(1, 10) if not ((z[r] | sp[c] | bl[r // 3 * 3 + c // 3]) >> v) & 1]
                if len(frei) < mgl:
                    beste, mgl, kand = i, len(frei), frei
                    if mgl == 0:
                        return False
        if beste is None:
            return True
        r, c = divmod(beste, 9)
        b = r // 3 * 3 + c // 3
        for v in kand:
            bit = 1 << v
            s[beste] = v
            z[r] |= bit; sp[c] |= bit; bl[b] |= bit
            if loese():
                return True
            z[r] ^= bit; sp[c] ^= bit; bl[b] ^= bit
            s[beste] = 0
        return False
    return "".join(map(str, s)) if loese() else None


@_reg("Algorithmen und Puzzle", "Kuerzesten Weg durch ein Text-Labyrinth finden (BFS)", 'lab = "#########\\n#S  #   #\\n# # # # #\\n# #   #E#\\n#########"\nlaenge, bild = labyrinth_loesen(lab)\nprint(laenge)\nprint(bild)')
def labyrinth_loesen(text):
    zeilen = [list(z) for z in text.split("\n")]
    start = ziel = None
    for y, z in enumerate(zeilen):
        for x, c in enumerate(z):
            if c == "S":
                start = (y, x)
            elif c == "E":
                ziel = (y, x)
    if not start or not ziel:
        raise ValueError("Das Labyrinth braucht S (Start) und E (Ende)")
    vor, q = {start: None}, collections.deque([start])
    while q:
        y, x = q.popleft()
        if (y, x) == ziel:
            break
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < len(zeilen) and 0 <= nx < len(zeilen[ny]) and zeilen[ny][nx] != "#" and (ny, nx) not in vor:
                vor[(ny, nx)] = (y, x)
                q.append((ny, nx))
    if ziel not in vor:
        return None, text
    p, n = vor[ziel], 0
    while p and p != start:
        zeilen[p[0]][p[1]] = "·"
        p = vor[p]
    weg, k = ziel, 0
    while weg != start:
        weg = vor[weg]
        k += 1
    return k, "\n".join("".join(z) for z in zeilen)


@_reg("Algorithmen und Puzzle", "Conways Spiel des Lebens (Text-Raster mit # und .)", 'glider = ".#...\\n..#..\\n###..\\n.....\\n....."\nprint(game_of_life(glider, 4))')
def game_of_life(raster, schritte=1, umlaufend=False):
    z = [list(r) for r in raster.split("\n")]
    h, b = len(z), len(z[0])
    for _ in range(schritte):
        neu = [["."] * b for _ in range(h)]
        for y in range(h):
            for x in range(b):
                n = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy or dx:
                            yy, xx = y + dy, x + dx
                            if umlaufend:
                                n += z[yy % h][xx % b] == "#"
                            elif 0 <= yy < h and 0 <= xx < b:
                                n += z[yy][xx] == "#"
                neu[y][x] = "#" if (n == 3 or (n == 2 and z[y][x] == "#")) else "."
        z = neu
    return "\n".join("".join(r) for r in z)


@_reg("Algorithmen und Puzzle", "Mandelbrot-Menge als ASCII-Kunst", 'print(mandelbrot_ascii(60, 20))')
def mandelbrot_ascii(breite=60, hoehe=24, max_iter=40):
    palette = " .:-=+*#%@"
    aus = []
    for j in range(hoehe):
        zeile = ""
        for i in range(breite):
            c = complex(-2.2 + 3.2 * i / breite, -1.2 + 2.4 * j / hoehe)
            z, n = 0j, 0
            while abs(z) <= 2 and n < max_iter:
                z = z * z + c
                n += 1
            zeile += "@" if n == max_iter else palette[n * (len(palette) - 2) // max_iter]
        aus.append(zeile)
    return "\n".join(aus)


@_reg("Algorithmen und Puzzle", "Huffman-Kodierung: Text komprimieren und wiederherstellen", 'codes, bits = huffman_kodieren("abracadabra alakazam")\nprint(len(bits), "Bit statt", 8 * 20)\nprint(huffman_dekodieren(bits, codes))')
def huffman_kodieren(text):
    if not text:
        return {}, ""
    haeufig = collections.Counter(text)
    zaehler = itertools.count()
    heap = [(n, next(zaehler), (c,)) for c, n in haeufig.items()]
    heapq.heapify(heap)
    codes = {c: "" for c in haeufig}
    if len(heap) == 1:
        codes[text[0]] = "0"
    while len(heap) > 1:
        n1, _, a = heapq.heappop(heap)
        n2, _, b = heapq.heappop(heap)
        for c in a:
            codes[c] = "0" + codes[c]
        for c in b:
            codes[c] = "1" + codes[c]
        heapq.heappush(heap, (n1 + n2, next(zaehler), a + b))
    return codes, "".join(codes[c] for c in text)


@_reg("Algorithmen und Puzzle", "Huffman-Bits zurueck in Text", 'c, b = huffman_kodieren("hallo")\nprint(huffman_dekodieren(b, c))')
def huffman_dekodieren(bits, codes):
    rueck = {v: k for k, v in codes.items()}
    aus, puffer = [], ""
    for b in bits:
        puffer += b
        if puffer in rueck:
            aus.append(rueck[puffer])
            puffer = ""
    if puffer:
        raise ValueError("Bitfolge passt nicht zur Code-Tabelle")
    return "".join(aus)


@_reg("Algorithmen und Puzzle", "N-Damen-Problem: erste Loesung und Anzahl", 'print(n_damen(8), n_damen_anzahl(8))')
def n_damen(n=8):
    def platz(zeile, spalten):
        if zeile == n:
            return spalten
        for c in range(n):
            if all(c != k and abs(c - k) != zeile - r for r, k in enumerate(spalten)):
                erg = platz(zeile + 1, spalten + [c])
                if erg:
                    return erg
        return None
    return platz(0, [])


def n_damen_anzahl(n=8):
    def zaehle(zeile, spalten):
        if zeile == n:
            return 1
        return sum(zaehle(zeile + 1, spalten + [c]) for c in range(n)
                   if all(c != k and abs(c - k) != zeile - r for r, k in enumerate(spalten)))
    return zaehle(0, [])


@_reg("Algorithmen und Puzzle", "Tuerme von Hanoi: alle Zuege", 'z = hanoi(4)\nprint(len(z), z[:3])')
def hanoi(n, von="A", nach="C", via="B"):
    if n == 0:
        return []
    return hanoi(n - 1, von, via, nach) + [(von, nach)] + hanoi(n - 1, via, nach, von)


@_reg("Algorithmen und Puzzle", "Wuerfeln mit Notation wie 3d6+2", 'print(wuerfeln("3d6+2", seed=7), wuerfeln("1d20", seed=7))')
def wuerfeln(ausdruck="1d6", seed=None):
    m = re.fullmatch(r"\s*(\d*)d(\d+)\s*([+-]\s*\d+)?\s*", ausdruck.lower())
    if not m:
        raise ValueError("Ungueltige Wuerfelnotation: " + ausdruck)
    anzahl, seiten = int(m[1] or 1), int(m[2])
    if anzahl < 1 or anzahl > 1000 or seiten < 2:
        raise ValueError("Wuerfelanzahl oder Seitenzahl ausserhalb des erlaubten Bereichs")
    r = random.Random(seed)
    return sum(r.randint(1, seiten) for _ in range(anzahl)) + int((m[3] or "0").replace(" ", ""))


@_reg("Algorithmen und Puzzle", "Sicheres Passwort erzeugen", 'print(len(passwort(20)), passwort_staerke(passwort(20)))')
def passwort(laenge=16, sonderzeichen=True):
    if laenge < 8:
        raise ValueError("Mindestens 8 Zeichen")
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits] + ([ "!@#$%&*?-_+=" ] if sonderzeichen else [])
    alle = "".join(pools)
    pw = [secrets.choice(p) for p in pools] + [secrets.choice(alle) for _ in range(laenge - len(pools))]
    secrets.SystemRandom().shuffle(pw)
    return "".join(pw)


@_reg("Algorithmen und Puzzle", "Passwortstaerke als Entropie in Bit mit Bewertung", 'print(passwort_staerke("hallo"), passwort_staerke("Tr0ub4dor&3xKq!9zL"))')
def passwort_staerke(pw):
    pool = 0
    for klasse, groesse in ((r"[a-z]", 26), (r"[A-Z]", 26), (r"\d", 10), (r"[^a-zA-Z0-9]", 32)):
        if re.search(klasse, pw):
            pool += groesse
    bits = round(len(pw) * math.log2(pool), 1) if pool else 0.0
    return bits, ("sehr schwach" if bits < 28 else "schwach" if bits < 50 else "ok" if bits < 70 else "stark" if bits < 100 else "sehr stark")


@_reg("Algorithmen und Puzzle", "Praefixbaum (Trie) fuer Autovervollstaendigung", 't = Trie()\nfor w in ["python", "pyramide", "pizza", "java"]:\n    t.einfuegen(w)\nprint(t.suche("py"))')
class Trie:
    def __init__(self):
        self._w = {}

    def einfuegen(self, wort):
        k = self._w
        for c in wort:
            k = k.setdefault(c, {})
        k["$"] = True

    def suche(self, praefix):
        k = self._w
        for c in praefix:
            if c not in k:
                return []
            k = k[c]
        erg = []

        def sammle(knoten, pfad):
            for c, kind in sorted(knoten.items()):
                if c == "$":
                    erg.append(praefix + pfad)
                else:
                    sammle(kind, pfad + c)
        sammle(k, "")
        return erg


# =============================================================================
# WERKZEUGE
# =============================================================================
@_reg("Werkzeuge", "Dekorator: Laufzeit einer Funktion ausgeben", '@zeit\ndef langsam():\n    return sum(range(10**6))\nprint(langsam())')
def zeit(fn):
    @functools.wraps(fn)
    def w(*a, **k):
        t = time.perf_counter()
        try:
            return fn(*a, **k)
        finally:
            print("⏱ %s: %.1f ms" % (fn.__name__, (time.perf_counter() - t) * 1000))
    return w


@_reg("Werkzeuge", "Dekorator: Funktion bei Fehlern automatisch wiederholen", 'versuche = []\n@wiederholen(versuche=3, pause=0)\ndef wackelig():\n    versuche.append(1)\n    if len(versuche) < 3:\n        raise ConnectionError("noch nicht")\n    return "klappt"\nprint(wackelig(), len(versuche))')
def wiederholen(versuche=3, pause=0.1, ausnahmen=(Exception,)):
    def deko(fn):
        @functools.wraps(fn)
        def w(*a, **k):
            for i in range(versuche):
                try:
                    return fn(*a, **k)
                except ausnahmen:
                    if i == versuche - 1:
                        raise
                    time.sleep(pause)
        return w
    return deko


@_reg("Werkzeuge", "Dekorator: Ergebnisse fuer n Sekunden zwischenspeichern", '@cache_ttl(60)\ndef teuer(x):\n    print("rechne ...")\n    return x * 2\nprint(teuer(4), teuer(4))')
def cache_ttl(sekunden):
    def deko(fn):
        speicher = {}

        @functools.wraps(fn)
        def w(*a, **k):
            schluessel = (a, tuple(sorted(k.items())))
            jetzt = time.monotonic()
            if schluessel in speicher and jetzt - speicher[schluessel][0] < sekunden:
                return speicher[schluessel][1]
            wert = fn(*a, **k)
            speicher[schluessel] = (jetzt, wert)
            return wert
        w.leeren = speicher.clear
        return w
    return deko


@_reg("Werkzeuge", "Dekorator: Funktion nur beim ersten Aufruf ausfuehren", '@einmal\ndef setup():\n    print("Setup laeuft")\n    return 42\nprint(setup(), setup())')
def einmal(fn):
    ergebnis = []

    @functools.wraps(fn)
    def w(*a, **k):
        if not ergebnis:
            ergebnis.append(fn(*a, **k))
        return ergebnis[0]
    return w


@_reg("Werkzeuge", "Stoppuhr als with-Block", 'with stoppuhr() as t:\n    sum(range(10**6))\nprint(t.sekunden < 5)')
class stoppuhr:
    def __enter__(self):
        self._t = time.perf_counter()
        self.sekunden = 0.0
        return self

    def __exit__(self, *exc):
        self.sekunden = time.perf_counter() - self._t
        return False


@_reg("Werkzeuge", "Funktionen vergleichen: schnellster Kandidat mit Tabelle", 'print(vergleiche({"sum": lambda: sum(range(10000)), "schleife": lambda: [i for i in range(10000)]}, n=20))')
def vergleiche(funktionen, n=5):
    zeilen = []
    for name, fn in funktionen.items():
        ts = []
        for _ in range(n):
            t = time.perf_counter()
            fn()
            ts.append((time.perf_counter() - t) * 1000)
        zeilen.append((name, min(ts), sum(ts) / len(ts)))
    zeilen.sort(key=lambda r: r[1])
    best = zeilen[0][1] or 1e-9
    return tabelle([[n_, "%.3f" % mi, "%.3f" % mw, "%.1fx" % (mi / best)] for n_, mi, mw in zeilen], ["Funktion", "min ms", "mittel ms", "relativ"])


@_reg("Werkzeuge", "Einfacher Event-Emitter (on, once, emit)", 'e = EventEmitter()\ne.on("gruss", lambda n: print("Hallo", n))\ne.emit("gruss", "Anna")')
class EventEmitter:
    def __init__(self):
        self._h = collections.defaultdict(list)

    def on(self, name, fn):
        self._h[name].append(fn)
        return fn

    def once(self, name, fn):
        def einmal_(*a, **k):
            self.off(name, einmal_)
            return fn(*a, **k)
        self._h[name].append(einmal_)
        return fn

    def off(self, name, fn):
        if fn in self._h[name]:
            self._h[name].remove(fn)

    def emit(self, name, *a, **k):
        return [fn(*a, **k) for fn in list(self._h[name])]


@_reg("Werkzeuge", "Zustandsautomat mit erlaubten Uebergaengen", 'a = Zustandsautomat("offen", {"offen": ["in_arbeit"], "in_arbeit": ["fertig", "offen"], "fertig": []})\na.wechsle("in_arbeit")\nprint(a.zustand, a.erlaubt())')
class Zustandsautomat:
    def __init__(self, start, uebergaenge):
        self.zustand, self._u, self.verlauf = start, uebergaenge, [start]

    def erlaubt(self):
        return list(self._u.get(self.zustand, []))

    def wechsle(self, neu):
        if neu not in self._u.get(self.zustand, []):
            raise ValueError("Uebergang %s -> %s nicht erlaubt (erlaubt: %s)" % (self.zustand, neu, self.erlaubt()))
        self.zustand = neu
        self.verlauf.append(neu)
        return neu


@_reg("Werkzeuge", "Graph mit BFS, DFS, Dijkstra, topologischer Sortierung", 'g = Graph()\ng.kante("A", "B", 4); g.kante("A", "C", 1); g.kante("C", "B", 2); g.kante("B", "D", 5)\nprint(g.dijkstra("A", "D"))')
class Graph:
    def __init__(self, gerichtet=False):
        self.gerichtet = gerichtet
        self.nachbarn = collections.defaultdict(dict)

    def kante(self, u, v, gewicht=1):
        self.nachbarn[u][v] = gewicht
        self.nachbarn.setdefault(v, {})
        if not self.gerichtet:
            self.nachbarn[v][u] = gewicht
        return self

    def bfs(self, start):
        gesehen, q, ordnung = {start}, collections.deque([start]), []
        while q:
            n = q.popleft()
            ordnung.append(n)
            for m in sorted(self.nachbarn[n]):
                if m not in gesehen:
                    gesehen.add(m)
                    q.append(m)
        return ordnung

    def dfs(self, start):
        gesehen, ordnung = set(), []

        def besuche(n):
            gesehen.add(n)
            ordnung.append(n)
            for m in sorted(self.nachbarn[n]):
                if m not in gesehen:
                    besuche(m)
        besuche(start)
        return ordnung

    def dijkstra(self, start, ziel):
        dist, vor, heap = {start: 0}, {}, [(0, start)]
        while heap:
            d, n = heapq.heappop(heap)
            if n == ziel:
                break
            if d > dist.get(n, math.inf):
                continue
            for m, w in self.nachbarn[n].items():
                nd = d + w
                if nd < dist.get(m, math.inf):
                    dist[m], vor[m] = nd, n
                    heapq.heappush(heap, (nd, m))
        if ziel not in dist:
            return math.inf, []
        pfad, n = [ziel], ziel
        while n != start:
            n = vor[n]
            pfad.append(n)
        return dist[ziel], pfad[::-1]

    def topologisch(self):
        grad = {n: 0 for n in self.nachbarn}
        for n in self.nachbarn:
            for m in self.nachbarn[n]:
                grad[m] += 1
        q = collections.deque(sorted(n for n, g in grad.items() if g == 0))
        erg = []
        while q:
            n = q.popleft()
            erg.append(n)
            for m in sorted(self.nachbarn[n]):
                grad[m] -= 1
                if grad[m] == 0:
                    q.append(m)
        if len(erg) != len(grad):
            raise ValueError("Der Graph enthaelt einen Zyklus")
        return erg


# =============================================================================
# WEB UND KI (nur im Browser: Python-IDE mit Pyodide)
# =============================================================================
@_reg("Web und KI", "Webadresse abrufen (JSON oder Text), mit await", 'daten = await holen("https://babybounce500.github.io/ki-academy-preview/gamma-pdfs/manifest.json")\nprint(len(daten), daten[0]["title"])')
async def holen(url, art="json"):
    from pyodide.http import pyfetch
    antwort = await pyfetch(url)
    if antwort.status >= 400:
        raise RuntimeError("Abruf fehlgeschlagen: HTTP %d fuer %s" % (antwort.status, url))
    return await (antwort.json() if art == "json" else antwort.string())


@_reg("Web und KI", "Gemini-KI direkt aus Python fragen (nutzt den Kurs-Zugang, mit await)", 'antwort = await frage_ki("Erklaere in zwei Saetzen, was eine Python-Liste ist.")\nprint(antwort)')
async def frage_ki(frage, system=None, modell="gemini-3.5-flash-lite", max_tokens=512):
    from pyodide.http import pyfetch
    body = {"contents": [{"role": "user", "parts": [{"text": str(frage)[:6000]}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.4}}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    antwort = await pyfetch("https://glow-up-gemini.replit.app/gemini/models/%s/generateContent" % modell,
                            method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(body))
    text = await antwort.string()
    if antwort.status >= 400:
        if "BUDGET" in text:
            raise RuntimeError("Das KI-Kontingent des Kurs-Zugangs ist gerade aufgebraucht. Bitte spaeter erneut versuchen.")
        if "INPUT_TOKEN_LIMIT" in text:
            raise RuntimeError("Die Frage ist zu lang fuer den Kurs-Zugang.")
        raise RuntimeError("KI-Abruf fehlgeschlagen (HTTP %d)" % antwort.status)
    teile = json.loads(text)["candidates"][0]["content"]["parts"]
    return "".join(t.get("text", "") for t in teile if not t.get("thought")).strip()


def _mpl():
    import matplotlib
    matplotlib.use("agg", force=True)
    import matplotlib.pyplot as plt
    return plt


@_reg("Web und KI", "Liniendiagramm mit einer Zeile (matplotlib)", 'linien(range(10), [i * i for i in range(10)], titel="Quadratzahlen")')
def linien(x, *ys, titel="", beschriftungen=None):
    plt = _mpl()
    plt.figure(figsize=(7, 4))
    for i, y in enumerate(ys):
        plt.plot(list(x), list(y), marker="o", label=(beschriftungen[i] if beschriftungen else None))
    if titel:
        plt.title(titel)
    if beschriftungen:
        plt.legend()
    plt.grid(alpha=.3)
    plt.show()


@_reg("Web und KI", "Balkendiagramm aus einem Dict", 'balken_plot({"Python": 48, "JavaScript": 40, "Rust": 12}, titel="Beliebtheit")')
def balken_plot(daten, titel=""):
    plt = _mpl()
    plt.figure(figsize=(7, 4))
    plt.bar(list(daten.keys()), list(daten.values()), color="#3b82f6")
    if titel:
        plt.title(titel)
    plt.grid(axis="y", alpha=.3)
    plt.show()


@_reg("Web und KI", "Tortendiagramm aus einem Dict", 'torte_plot({"Miete": 900, "Essen": 350, "Sparen": 250}, titel="Budget")')
def torte_plot(daten, titel=""):
    plt = _mpl()
    plt.figure(figsize=(5, 5))
    plt.pie(list(daten.values()), labels=list(daten.keys()), autopct="%1.0f%%", startangle=90)
    if titel:
        plt.title(titel)
    plt.show()


# =============================================================================
# UEBERSICHT UND SELBSTTEST
# =============================================================================
def katalog():
    """Liste aller Funktionen mit Kategorie, Beschreibung und Beispielcode."""
    return sorted(_KATALOG, key=lambda e: (e["kategorie"], e["name"]))


def hilfe(kategorie=None):
    """Zeigt alle Funktionen nach Kategorie. Mit Kategorie-Namen nur diese."""
    aktuell = None
    for e in katalog():
        if kategorie and kategorie.lower() not in e["kategorie"].lower():
            continue
        if e["kategorie"] != aktuell:
            aktuell = e["kategorie"]
            print("\n== %s ==" % aktuell)
        print("  %-22s %s" % (e["name"], e["beschreibung"]))
    print("\n%d Funktionen. Beispielcode: vibe.katalog()[i]['beispiel']" % len([e for e in katalog() if not kategorie or kategorie.lower() in e["kategorie"].lower()]))


def demo():
    """Kleine Schau der beeindruckendsten Funktionen."""
    print(mandelbrot_ascii(60, 16))
    print()
    print(tabelle([[n, zahl_zu_wort(n)] for n in (7, 42, 1999, 1234567)], ["Zahl", "in Worten"]))
    print()
    print(balken({"Python": 48, "JavaScript": 40, "Rust": 12}))
    print()
    print("Feiertage NRW 2025:", ", ".join("%s %s" % (d.strftime("%d.%m."), n) for d, n in feiertage(2025, "NW").items()))
    print("Sparkline:", sparkline([1, 3, 2, 8, 5, 9, 4, 6]))


__all__ = [e["name"] for e in _KATALOG] + ["n_damen_anzahl", "katalog", "hilfe", "demo", "BUNDESLAENDER"]
