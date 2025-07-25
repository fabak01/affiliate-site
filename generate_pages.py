import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# ── Helper: Cache & fetch tool blurbs via the new chat.completions endpoint ──
def get_tool_blurb(tool_name):
    df_cache = pd.read_csv("tool_blurbs.csv")
    match = df_cache[df_cache.tool_name == tool_name]
    if not match.empty:
        return match.iloc[0].blurb
    # Fallback if missing:
    return f"Discover why {tool_name} could be the right choice for you."


# ── Load data files ─────────────────────────────────────────────────────────
df_phrases = pd.read_csv("keywords.csv")
df_tools   = pd.read_csv("tools.csv")
df_feats   = pd.read_csv("features.csv")

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
template = env.get_template("page.html")
os.makedirs("dist", exist_ok=True)

# ── Generate one page per keyword ──────────────────────────────────────────
seeds = list(tools_map.keys())
for _, row in df_phrases.iterrows():
    phrase = row["phrase"]
    seed = next((s for s in seeds if s in phrase.lower()), seeds[0])

    raw_tools = tools_map.get(seed, [])
    tools = []
    for name, link in raw_tools:
        blurb = get_tool_blurb(name)
        tools.append({"name":name, "link":link, "blurb":blurb})

    feats_dict = feats_map.get(seed, {})
    features = [feats_dict[k] for k in sorted(feats_dict) if feats_dict[k]]

    slug = phrase.lower().replace(" ", "-").replace("/", "-")
    out_path = os.path.join("dist", f"{slug}.html")

    html = template.render(
        phrase=phrase,
        year=datetime.now().year,
        tools=tools,
        features=features
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

print(f"✅ Generated {len(df_phrases)} pages with dynamic blurbs in dist/")
