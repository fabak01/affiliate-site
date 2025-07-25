import requests
import pandas as pd
from urllib.parse import quote

# 1. Våre seed-kategorier
seed_categories = [
    'passordhvelv', 'e-signatur', 'CRM',
    'e-postmarkedsføring', 'helpdesk',
    'prosjektstyring', 'fakturering',
    'HRM', 'VPN', 'cloud storage'
]

def fetch_suggestions(seed):
    """Henter Google Autocomplete-forslag for et gitt seed."""
    url = (
      'https://suggestqueries.google.com/complete/search'
      '?client=firefox&hl=nb&q=' + quote(seed)
    )
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()[1]  # Liste med forslag
    else:
        return []

all_phrases = []

# 2. Hent forslag for hver seed + bygg “for bedrift”, “pris”, “gratis”
suffixes = [
    '', ' for bedrift', ' pris', ' gratis', ' alternativer', ' beste', ' i 2025',
    ' enterprise', ' oppsett', ' guide', ' tutorial', ' dokumentasjon', ' vs konkurrent',
    ' anmeldelse', ' sammenligning', ' fordeler og ulemper', ' erfaringer', ' pros and cons',
    ' anbefaling', ' brukerveiledning', ' casestudie', ' kundesupport', ' sikkerhet',
    ' integrasjoner', ' prissammenligning', ' brukstilfeller', ' nybegynnerguide',
    ' avansert'
]

for seed in seed_categories:
    suggestions = fetch_suggestions(seed)
    for base in suggestions:
        for suf in suffixes:
            phrase = f"{base}{suf}".strip()
            all_phrases.append({'phrase': phrase})

# 3. Lag “vs”-par mellom seedene
for i, s1 in enumerate(seed_categories):
    for s2 in seed_categories[i+1:]:
        all_phrases.append({'phrase': f"{s1} vs {s2}"})
        all_phrases.append({'phrase': f"{s2} vs {s1}"})

# 4. Deduper og skriv til CSV
df = pd.DataFrame(all_phrases).drop_duplicates().reset_index(drop=True)
df.to_csv('keywords.csv', index=False)
print(f"✅ Genererte {len(df)} unike fraser – se keywords.csv")

