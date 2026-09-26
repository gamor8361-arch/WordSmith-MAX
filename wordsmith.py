#!/usr/bin/env python3
"""
WordSmith MAX - Générateur de wordlists personnalisées ultra-complet.
Analyse psychologique des schémas de mots de passe réels :
  - Mot + année de naissance / mariage
  - Mot + séquences numériques (123, 1234, 123456...)
  - Clavier (qwerty, azerty, !@#$)
  - Leetspeak multi-niveaux, toutes les casses, mots inversés
  - Tous les formats de dates (JJ/MM/AAAA, MMAAAA, AAAA, etc.)
  - Combinaisons multi-mots avec séparateurs
Pour tests de sécurité autorisés uniquement.
"""

import argparse
import itertools
import re
import sys
from datetime import datetime

# ============================================================
# 1. PROFIL : maximum d'infos sur la cible
# ============================================================
FIELDS = {
    "firstname":  "Prénom",
    "lastname":   "Nom",
    "nickname":   "Surnom / pseudo",
    "pet":        "Animal favori",
    "company":    "Entreprise",
    "city":       "Ville",
    "country":    "Pays",
    "child":      "Enfant",
    "partner":    "Conjoint(e)",
    "hobby":      "Loisir",
    "sport":      "Sport / équipe",
    "food":       "Nourriture / boisson",
    "music":      "Artiste / chanteur",
    "movie":      "Film / série",
    "school":     "École / université",
    "street":     "Rue",
    "phone":      "Téléphone (derniers chiffres)",
    "favnum":     "Chiffre favori",
    "car":        "Voiture / marque",
    "word":       "Mot favori / devise",
    "birthdate":  "Date de naissance (JJ/MM/AAAA)",
    "wedding":    "Date mariage (JJ/MM/AAAA)",
}

def interactive_profile():
    print("[*] Mode interactif — laissez vide pour ignorer.\n")
    p = {}
    for key, label in FIELDS.items():
        val = input(f"  {label} [{key}]: ").strip()
        if val:
            p[key] = val
    return p

# ============================================================
# 2. MUTATIONS — analyse psychologique des schémas réels
# ============================================================
LEET_LEVELS = {
    1: {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"},
    2: {"a": "@", "e": "3", "i": "1", "o": "0", "s": "$", "t": "+",
        "b": "8", "g": "9", "l": "1", "z": "2"},
}

KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "azertyuiop",
                 "qsdfghjklm", "wxcvbn", "1234567890", "!@#$%^&*()"]
KEYBOARD_WORDS = ["qwerty", "azerty", "qwertz", "asdf", "zxcvbn",
                  "poiuy", "lkjhg", "1234", "abcd"]

NUMBER_PATTERNS = [
    "1", "12", "123", "1234", "12345", "123456", "1234567",
    "12345678", "123456789", "1234567890", "12345678910",
    "0", "00", "01", "02", "007", "69", "666", "777", "123321",
    "1111", "0000", "100", "2000", "2001", "111111",
]
SYMBOL_SUFFIX = ["!", "!!", ".", "?", "#", "$", "@", "*", "_", "-",
                 "!", "?", "1", "1!", "!1", "@1", "!!1", "!!1!"]

def case_variants(w: str):
    """Toutes les casses plausibles."""
    return {w, w.lower(), w.upper(), w.capitalize(),
            w.title().replace(" ", ""), w.swapcase()}

def leet_variants(w: str, level: int = 1):
    """Toutes les substitutions leet possibles (combinatoire complète)."""
    subs = LEET_LEVELS[level]
    results = {w}
    changed = True
    while changed:
        changed = False
        new = set()
        for word in results:
            for i, c in enumerate(word):
                if c.lower() in subs:
                    new.add(word[:i] + subs[c.lower()] + word[i+1:])
        if new - results:
            results |= new
            changed = True
    return results

def reverse(w: str):
    return w[::-1]

def double(w: str):
    return w + w

def date_tokens(date_str: str):
    """Tous les formats de dates réels observés chez les utilisateurs."""
    out = set()
    m = re.match(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", date_str)
    if not m:
        return out
    d, mo, y = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
    yy = y[-2:]
    dm, md = d + mo, mo + d
    d1, m1 = str(int(d)), str(int(mo))
    patterns = [
        y, yy, d, mo, dm, md, d1 + m1, m1 + d1,
        dm + y, md + y, dm + yy, md + yy, y + dm, y + md,
        f"{d}/{mo}", f"{d}-{mo}", f"{d}.{mo}",
        f"{d}/{mo}/{y}", f"{d}-{mo}-{y}", f"{d}.{mo}.{y}",
        d1 + m1 + y, m1 + d1 + y, d1 + m1 + yy, y + m1 + d1,
        f"{mo}/{d}", f"{mo}-{d}",
        datetime(2000, int(mo), int(d)).strftime("%d%m") if
        _valid_date(y, mo, d) else "",
        datetime(2000, int(mo), int(d)).strftime("%d%B") if
        _valid_date(y, mo, d) else "",
    ]
    out |= {p for p in patterns if p}
    return out

def _valid_date(y, mo, d):
    try:
        datetime(int(y), int(mo), int(d))
        return True
    except ValueError:
        return False

# ============================================================
# 3. GÉNÉRATION COMBINATOIRE — par chunks (millions d'entrées)
# ============================================================
def mutate_word(w: str, leet_level: int):
    """Applique TOUTES les mutations à un mot de base."""
    out = set()
    for c in case_variants(w):
        out.add(c)
        out.add(reverse(c))
        out.add(double(c))
        out |= leet_variants(c, leet_level)
        if len(c) <= 20:
            out |= leet_variants(reverse(c), leet_level)
    return out

def suffixes_for(profile: dict):
    """Suffixes psychologiques : dates, chiffres, clavier, symboles."""
    s = set(NUMBER_PATTERNS)
    s |= {w.upper() for w in KEYBOARD_WORDS}
    s |= {w.capitalize() for w in KEYBOARD_WORDS}
    s |= {"!", "1!", "!!", "!1", "123!", "!!1"}
    for field in ("birthdate", "wedding"):
        if profile.get(field):
            s |= date_tokens(profile[field])
    for num in (profile.get("phone", ""), profile.get("favnum", "")):
        if num:
            s |= {num, num + num}
    # Années voisines de la naissance
    bd = profile.get("birthdate", "")
    if re.match(r"\d{1,2}/\d{1,2}/(\d{4})", bd):
        y = int(re.match(r"\d{1,2}/\d{1,2}/(\d{4})", bd).group(1))
        s |= {str(n) for n in range(y - 3, y + 4)}
    return {x for x in s if x}

def generate_chunks(profile: dict, min_len: int, max_len: int,
                    combos: int, leet_level: int, chunk_size: int = 200000):
    """Générateur paresseux : yield des chunks pour supporter des millions."""
    seen = set()

    def dedup_add(cands):
        fresh = []
        for c in cands:
            c = c[:max_len]
            if len(c) >= min_len and c not in seen:
                seen.add(c)
                fresh.append(c)
        return fresh

    bases = set()
    for key in FIELDS:
        if key in ("birthdate", "wedding", "phone", "favnum"):
            continue
        val = profile.get(key, "").strip()
        if val:
            for part in re.split(r"[ ,;/]+", val):
                if part:
                    bases |= case_variants(part)
    # Combinaisons prénom+nom : JohnDoe, DoeJohn, JD, j.doe...
    f, l = profile.get("firstname", ""), profile.get("lastname", "")
    if f and l:
        bases |= case_variants(f + l) | case_variants(l + f)
        bases |= case_variants(f[0] + l) | case_variants(l + f[0])
        bases |= case_variants(f + "." + l) | case_variants(f + "_" + l)
        bases |= case_variants(f[0] + l[0])

    # --- PHASE 1 : mots mutés seuls
    for b in bases:
        yield dedup_add(mutate_word(b, leet_level))

    # --- PHASE 2 : mot + suffixe (mot+année, mot+123, etc.)
    suffixes = sorted(suffixes_for(profile))
    for b in sorted(bases):
        for w in mutate_word(b, leet_level):
            cands = [w + s for s in suffixes]
            cands += [s + w for s in suffixes]          # année+mot
            cands += [w + s + "!" for s in suffixes]    # mot+123!
            yield dedup_add(cands)

    # --- PHASE 3 : combinaisons multi-mots
    base_list = sorted(bases)
    if len(base_list) > 40:
        base_list = base_list[:40]
    suffixes = list(suffixes)[:60]
    for n in range(2, combos + 1):
        for combo in itertools.permutations(base_list, n):
            for sep in ("", ".", "_", "-"):
                word = sep.join(combo)
                if len(word) > max_len:
                    continue
                cands = [word]
                for w in mutate_word(word, leet_level):
                    cands.append(w)
                    for s in suffixes:
                        cands.append(w + s)
                yield dedup_add(cands)

# ============================================================
# 4. MAIN
# ============================================================
def main():
    ap = argparse.ArgumentParser(description="WordSmith MAX generator")
    for key, label in FIELDS.items():
        ap.add_argument(f"--{key}", help=label)
    ap.add_argument("-i", "--interactive", action="store_true",
                    help="Remplir le profil en mode interactif")
    ap.add_argument("-m", "--min", type=int, default=4)
    ap.add_argument("-M", "--max", type=int, default=24)
    ap.add_argument("-C", "--combos", type=int, default=3)
    ap.add_argument("-L", "--leet", type=int, default=2, choices=[0, 1, 2],
                    help="0=off 1=basique 2=agressif")
    ap.add_argument("-o", "--output", default="wordlist.txt")
    args = ap.parse_args()

    profile = {k: v for k, v in vars(args).items() if k in FIELDS and v}
    if args.interactive:
        profile.update(interactive_profile())
    if not profile:
        ap.error("Aucune information fournie. Utilisez -i ou des arguments.")

    print(f"[*] Profil : {profile}")
    total = 0
    with open(args.output, "w", encoding="utf-8", errors="ignore") as fh:
        for chunk in generate_chunks(profile, args.min, args.max,
                                     args.combos, args.leet):
            fh.write("\n".join(chunk) + "\n")
            total += len(chunk)
            sys.stdout.write(f"\r[+] {total:,} mots de passe générés...")
            sys.stdout.flush()
    print(f"\n[✓] {total:,} mots de passe écrits dans {args.output}")

if __name__ == "__main__":
    main()