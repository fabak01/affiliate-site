import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# ── Load data files ─────────────────────────────────────────────────────────
df_phrases = pd.read_csv("keywords.csv")
df_tools   = pd.read_csv("tools.csv")
df_feats   = pd.read_csv("features.csv")
# If you stub blurbs locally, you can skip openai imports here

# Build maps (as before)
tools_map = (
    df_tools
      .groupby("seed")[["tool_name","affiliate_link"]]
      .apply(lambda d: list(d.itertuples(index=False, name=None)))
      .to_dict()
)
feats_map = (
    df_feats
      .set_index("seed")
      .to_dict(orient="index")
)

# ── Prepare Jinja2 ──────────────────────────────────────────────────────────
env = Environment(loader=FileSystemLoader("templates"))
page_tmpl  = env.get_template("page.html")
index_tmpl = env.get_template("index.html")

# Ensure output dir exists
os.makedirs("dist", exist_ok=True)

# ── Generate subpages and collect page info ────────────────────────────────
seeds = list(tools_map.keys())
pages = []

for _, row in df_phrases.iterrows():
    phrase = row["phrase"]
    seed   = next((s for s in seeds if s in phrase.lower()), seeds[0])

    # tools & features as before (stubbed or via get_tool_blurb)
    raw_tools = tools_map.get(seed, [])
    tools = [{"name":n,"link":l,"blurb":""} for n,l in raw_tools]  # remove blurb if you stub

    feats_dict = feats_map.get(seed, {})
    features = [feats_dict[k] for k in sorted(feats_dict) if feats_dict[k]]

    # slugify phrase
    slug = phrase.lower().replace(" ", "-").replace("/", "-")

    # render page.html → dist/<slug>.html
    html = page_tmpl.render(
        phrase=phrase,
        year=datetime.now().year,
        tools=tools,
        features=features
    )
    out_file = os.path.join("dist", f"{slug}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    # collect for index
    pages.append({"slug": slug, "phrase": phrase})

print(f"✅ Generated {len(pages)} subpages in dist/")

# ── Render index.html → dist/index.html ────────────────────────────────────
index_html = index_tmpl.render(pages=pages)
with open(os.path.join("dist","index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("✅ Generated homepage at dist/index.html")
