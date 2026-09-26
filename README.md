# WordSmith
Personalized password wordlist generator for authorized penetration tests
and password audits. Inspired by CUPP.

## Usage
python3 wordsmith.py -f John -l Doe -b 14/03/1990 -p Rex -c Acme -o list.txt

## Options
-f first name   -l last name   -n nickname   -p pet   -c company
-i city         -k child       -a partner    -H hobby
-b birthdate (DD/MM/YYYY)      -u favorite number
-m/-M min/max length   -C max word combinations   -o output file

## Legal
Only use against systems you are explicitly authorized to test.