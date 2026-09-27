# WordSmith MAX

**Custom wordlist generator** for authorized penetration testing and password audits. Written in pure Python with zero external dependencies.

Inspired by tools like [CUPP](https://github.com/Mebus/cupp), WordSmith MAX combines target OSINT details with real-world password psychology to generate realistic candidate lists.

---

## Features

- **Comprehensive OSINT Profile**: Names, dates, pets, partners, hobbies, street, phone numbers, and custom words.
- **Password Psychology Engine**: Pattern rules derived from breach data analysis:
  - `Word` + birth year (`john2000`) and neighboring years
  - `Word` + numerical sequences (`john123`, `john12345678910`)
  - Keyboard walks (`johnqwerty`, `johnazerty`, `john!@#$`)
  - Symbol decorations (`john!!1`, `john2000!`, `john#`)
  - Date permutations across all common formats (`14032000`, `14/03`, `03142000`...)
- **Mutations & Combinations**:
  - Full casing variations, reversal, and doubling
  - Multi-level Leetspeak substitution
  - Up to 3-token multi-word combinations using custom delimiters (`.`, `_`, `-`)
- **Memory Efficient**: Streaming generator pattern writes output in chunks without memory exhaustion.

---

## Quick Start

### Interactive Mode (Recommended)
```bash
python wordsmith.py -i -o wordlist.txt

# Basic profile generation
python wordsmith.py -f john -l doe -p rex -t paris -d 14/03/2000 -o john.txt

# Generation capped at 1,000,000 candidates
python wordsmith.py -f ahmed -l sam -p Rex -N 1000000 -o wordlist.txt
