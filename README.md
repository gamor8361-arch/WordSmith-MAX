# WordSmith MAX

**Generateur de wordlists (listes de mots de passe) personnalisees** pour
tests d'intrusion autorises et audits de mots de passe. Ecrit en Python pur,
sans dependance externe.

Inspire de [CUPP](https://github.com/Mebus/cupp), WordSmith MAX va beaucoup
plus loin : il combine des donnees OSINT sur une personne avec la
psychologie reelle des mots de passe pour produire des millions de candidats
realistes.

---

## Fonctionnalites

- **Profil OSINT complet** : prenom, nom, surnom, animal, entreprise, ville,
  pays, enfant, conjoint, loisir, sport, nourriture, musique, film, ecole,
  rue, telephone, chiffre favori, voiture, devise, date de naissance, date de
  mariage.
- **Moteur de psychologie des mots de passe** (schemas observes dans de
  vraies fuites de donnees) :
  - `Mot` + annee de naissance (`john2000`) et annees voisines
  - `Mot` + suites numeriques (`john123`, `john12345678910`)
  - Promenades clavier (`johnqwerty`, `johnazerty`, `john!@#$`)
  - Decorations de symboles (`john!!1`, `john2000!`, `john#`)
  - Dates dans tous les formats reels (`14032000`, `14/03`, `03142000`...)
- **Toutes les mutations** sur chaque mot :
  - Toutes les casses (`john`, `JOHN`, `John`, `jOhN`...)
  - Inverse (`nhoj`) et double (`johnjohn`)
  - Leetspeak multi-niveaux (`J0hn`, `J0hN`, `J0hn_d03`...)
- **Combinaisons multi-mots** jusqu'a 3 tokens avec ``,`` `.` `_` `-`
  (`john.doe2000`, `DoeJohn123!`)
- **Sortie en streaming** : ecriture par chunks -> genere des millions
  d'entrees sans saturer la RAM.
- **Limite optionnelle** (`-N`) et compteur de progression en direct.

---

## Installation

```bash
git clone https://github.com/<ton-username>/wordsmith.git
cd wordsmith
python wordsmith.py -i
