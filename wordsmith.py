#!/usr/bin/env python3
"""
WordSmith MAX - Generateur de wordlists personnalisees ultra-complet.
Analyse psychologique des schemas de mots de passe reels :
  - Mot + annee de naissance / mariage
  - Mot + sequences numeriques (123, 1234, 123456...)
  - Clavier (qwerty, azerty, !@#$)
  - Leetspeak multi-niveaux, toutes les casses, mots inverses
  - Tous les formats de dates (JJ/MM/AAAA, MMAAAA, AAAA, etc.)
  - Combinaisons multi-mots avec separateurs
Pour tests de securite autorises uniquement.
"""

import argparse
import itertools
import os
import re
import sys
from datetime import datetime

# ============================================================
# 1. PROFIL : maximum d'infos sur la cible
#    clé interne -> (option courte, libellé)
# ============================================================
FIELDS = {
    "firstname": ("f", "Prenom"),
    "lastname":  ("l", "Nom"),
    "nickname":  ("n", "Surnom / pseudo"),
    "pet":       ("p", "Animal favori"),
    "company":   ("c", "Entreprise"),
    "city":      ("t", "Ville (town)"),
    "country":   ("y", "Pays"),
    "child":     ("k", "Enfant (kid)"),
    "partner":   ("a", "Conjoint(e)"),
    "hobby":     ("b", "Loisir"),
    "sport":     ("s", "Sport / equipe"),
    "food":      ("g", "Nourriture / boisson"),
    "music":     ("u", "Artiste / chanteur"),
    "movie":     ("e", "Film / serie"),
    "school":    ("h", "Ecole / universite"),
    "street":    ("r", "Rue (road)"),
    "phone":     ("j", "Telephone (derniers chiffres)"),
    "favnum":    ("q", "Chiffre favori"),
    "car":       ("w", "Voiture / marque"),
    "word":      ("x", "Mot favori / devise"),
    "birthdate": ("d", "Date de naissance (JJ/MM/AAAA)"),
    "wedding":   ("z", "Date mariage (JJ/MM/AAAA)"),
}


def interactive_profile():
    print("[*] Mode interactif - laissez vide pour ignorer.\n")
    p = {}
    for key, (_flag, label) in FIELDS.items():
        val = input(f"  {label} [-{_flag}]: ").strip()
        if val:
            p[key] = val
    return p


# ============================================================
# 2. MUTATIONS - analyse psychologique des schemas reels
# ============================================================
LEET_LEVELS = {
    1: {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"},
    2: {"a": "@", "e": "3", "i": "1", "o": "0", "s": "$", "t": "+",
        "b": "8", "g": "9", "l": "1", "z": "2"},
}

KEYBOARD_WORDS = ["qwerty", "azerty", "qwertz", "asdf", "zxcvbn",
                  "poiuy", "lkjhg", "1234", "abcd"]

NUMBER_PATTERNS = [
    "1", "12", "123", "1234", "12345", "123456", "1234567",
    "12345678", "123456789", "1234567890", "12345678910",
    "0", "00", "01", "02", "007", "69", "666", "777", "123321",
    "1111", "0000", "100", "2000", "2001", "111111",
]
SYMBOL_SUFFIX = ["!", "!!", ".", "?", "#", "$", "@", "*", "_", "-",
                 "1", "1!", "!1", "@1", "!!1", "!!1!"]


def case_variants(w: str):
    """Toutes les casses plausibles."""
    return {w, w.lower(), w.upper(), w.capitalize(),
            w.title().replace(" ", ""), w.swapcase()}


def leet_variants(w: str, level: int = 1):
    """Toutes les substitutions leet possibles (combinatoire complete)."""
    subs = LEET_LEVELS[level]
    results = {w}
    changed = True
    while changed:
        changed = False
        new = set()
        for word in results:
            for i, c in enumerate(word):
                if c.lower() in subs:
                    new.add(word[:i] + subs[c.lower()] + word[i + 1:])
        if new - results:
            results |= new
            changed = True
    return results


def _valid_date(y, mo, d):
    try:
        datetime(int(y), int(mo), int(d))
        return True
    except ValueError:
        return False


def date_tokens(date_str: str):
    """Tous les formats de dates reels observes chez les utilisateurs."""
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
    ]
    if _valid_date(y, mo, d):
        patterns.append(d + mo)
    out |= {p for p in patterns if p}
    return out


# ============================================================
# 3. GENERATION COMBINATOIRE - par chunks
# ============================================================
def mutate_word(w: str, leet_level: int):
    """Applique TOUTES les mutations a un mot de base."""
    out = set()
    for c in case_variants(w):
        out.add(c)
        out.add(c[::-1])
        out.add(c + c)
        out |= leet_variants(c, leet_level)
        if leet_level > 0 and len(c) <= 20:
            out |= leet_variants(c[::-1], leet_level)
    return out


def suffixes_for(profile: dict):
    """Suffixes psychologiques : dates, chiffres, clavier, symboles."""
    s = set(NUMBER_PATTERNS)
    s |= {w.upper() for w in KEYBOARD_WORDS}
    s |= {w.capitalize() for w in KEYBOARD_WORDS}
    s |= set(SYMBOL_SUFFIX)
    for field in ("birthdate", "wedding"):
        if profile.get(field):
            s |= date_tokens(profile[field])
    for num in (profile.get("phone", ""), profile.get("favnum", "")):
        if num:
            s |= {num, num + num}
    bd = profile.get("birthdate", "")
    m = re.match(r"\d{1,2}/\d{1,2}/(\d{4})", bd)
    if m:
        y = int(m.group(1))
        s |= {str(n) for n in range(y - 3, y + 4)}
    return {x for x in s if x}


def base_tokens(profile: dict):
    """Mots de base extraits du profil."""
    bases = set()
    for key in FIELDS:
        if key in ("birthdate", "wedding", "phone", "favnum"):
            continue
        val = profile.get(key, "").strip()
        if val:
            for part in re.split(r"[ ,;/]+", val):
                if part:
                    bases |= case_variants(part)
    f, l = profile.get("firstname", ""), profile.get("lastname", "")
    if f and l:
        bases |= case_variants(f + l) | case_variants(l + f)
        bases |= case_variants(f[0] + l) | case_variants(l + f[0])
        bases |= case_variants(f + "." + l) | case_variants(f + "_" + l)
        bases |= case_variants(f[0] + l[0])
    return bases


def generate_chunks(profile: dict, min_len: int, max_len: int,
                    combos: int, leet_level: int):
    """Generateur paresseux : yield des chunks dedupliques localement."""
    bases = base_tokens(profile)
    suffixes = sorted(suffixes_for(profile))

    def dedup_add(cands):
        """Deduplication LOCALE au chunk (memoire constante)."""
        trimmed = []
        for c in cands:
            c = c[:max_len]
            if len(c) >= min_len:
                trimmed.append(c)
        return list(dict.fromkeys(trimmed))

    # --- PHASE 1 : mots mutes seuls
    for b in bases:
        yield dedup_add(mutate_word(b, leet_level))

    # --- PHASE 2 : mot + suffixe (mot+annee, mot+123, etc.)
    for b in sorted(bases):
        for w in mutate_word(b, leet_level):
            cands = [w + s for s in suffixes]
            cands += [s + w for s in suffixes]           # annee+mot
            cands += [w + s + "!" for s in suffixes]     # mot+123!
            yield dedup_add(cands)

    # --- PHASE 3 : combinaisons multi-mots
    base_list = sorted(bases)
    if len(base_list) > 40:
        base_list = base_list[:40]
    suffix_list = suffixes[:60]
    for n in range(2, combos + 1):
        for combo in itertools.permutations(base_list, n):
            for sep in ("", ".", "_", "-"):
                word = sep.join(combo)
                if len(word) > max_len:
                    continue
                cands = [word]
                for w in mutate_word(word, leet_level):
                    cands.append(w)
                    for s in suffix_list:
                        cands.append(w + s)
                yield dedup_add(cands)


# ============================================================
# 4. MAIN
# ============================================================
def main():
    ap = argparse.ArgumentParser(
        description="WordSmith MAX - generateur de wordlists personnalisees",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Champs du profil (options courtes uniquement)
    for key, (flag, label) in FIELDS.items():
        ap.add_argument(f"-{flag}", dest=key, metavar="", help=label)

    # Options de controle
    ap.add_argument("-i", "--interactive", action="store_true",
                    help="Remplir le profil en mode interactif")
    ap.add_argument("-m", dest="min", type=int, default=4, metavar="",
                    help="Longueur minimale (defaut 4)")
    ap.add_argument("-M", dest="max", type=int, default=24, metavar="",
                    help="Longueur maximale (defaut 24)")
    ap.add_argument("-C", dest="combos", type=int, default=3, metavar="",
                    help="Nb max de mots combines (defaut 3)")
    ap.add_argument("-L", dest="leet", type=int, default=2,
                    choices=[0, 1, 2], metavar="",
                    help="0=off 1=basique 2=agressif (defaut 2)")
    ap.add_argument("-N", dest="limit", type=int, default=0, metavar="",
                    help="Nb max de mots de passe (0 = illimite)")
    ap.add_argument("-o", dest="output", default="wordlist.txt", metavar="",
                    help="Fichier de sortie (defaut wordlist.txt)")

    args = ap.parse_args()

    profile = {k: v for k, v in vars(args).items()
               if k in FIELDS and v}
    if args.interactive:
        profile.update(interactive_profile())
    if not profile:
        ap.error("Aucune information fournie. Utilisez -i ou des options "
                 "comme -f, -l, -p...")

    print(f"[*] Profil : {profile}")
    if args.limit:
        print(f"[*] Limite fixee a {args.limit:,} mots de passe.")

    total = 0
    limit = args.limit
    tmp_file = args.output + ".tmp"

    with open(tmp_file, "w", encoding="utf-8", errors="ignore") as fh:
        stop = False
        for chunk in generate_chunks(profile, args.min, args.max,
                                     args.combos, args.leet):
            if limit and total + len(chunk) > limit:
                chunk = chunk[:limit - total]   # coupe pile a la limite
                stop = True
            fh.write("\n".join(chunk) + "\n")
            total += len(chunk)
            sys.stdout.write(f"\r[+] {total:,} mots de passe generes...")
            sys.stdout.flush()
            if stop:
                break

    print(f"\n[*] Generation terminee : {total:,} lignes brutes.")

    # Si une limite est fixee : pas de gros tri final (gain temps/RAM)
    if limit:
        os.replace(tmp_file, args.output)
        print(f"[OK] {total:,} mots de passe ecrits dans {args.output}")
        return

    print("[*] Deduplication finale (peut consommer de la RAM pour les "
          "tres gros fichiers)...")
    try:
        with open(tmp_file, "r", encoding="utf-8", errors="ignore") as fin:
            lines = sorted(set(fin))
        with open(args.output, "w", encoding="utf-8", errors="ignore") as fout:
            fout.writelines(lines)
        os.remove(tmp_file)
        print(f"[OK] {len(lines):,} mots de passe uniques ecrits dans "
              f"{args.output}")
    except MemoryError:
        os.replace(tmp_file, args.output)
        print(f"[!] Memoire insuffisante pour dedupliquer - fichier brut "
              f"conserve ({total:,} lignes, possibles doublons).")
        print("    Astuce Windows : Get-Content wordlist.txt | "
              "Sort-Object -Unique | Set-Content wordlist_unique.txt")


if __name__ == "__main__":
    main()
