"""Builds the static, in-browser version of the app (stlite) into site/ from the code repository."""
import json
import shutil
from pathlib import Path

SRC = Path.home() / "spaceapps" / "gravity-readiness"
OUT = Path(__file__).parent / "site"
STLITE = "https://cdn.jsdelivr.net/npm/@stlite/browser@1.12.0/build"
INCLUDE = ["app.py", "ASSUMPTIONS.md", "readiness", "params", "data/demo", "data/osdr", ".streamlit/config.toml"]

if OUT.exists():
    shutil.rmtree(OUT)
files = []
for item in INCLUDE:
    src = SRC / item
    paths = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    for p in paths:
        rel = p.relative_to(SRC).as_posix()
        dst = OUT / "app" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        files.append(rel)

def served(rel):
    """Published name: no dot-directories (GitHub Pages) and no .md files (the documentation build renders them)."""
    return rel.replace(".streamlit/", "streamlit_").replace("ASSUMPTIONS.md", "ASSUMPTIONS.txt")


for rel in files:
    if served(rel) != rel:
        (OUT / "app" / rel).rename(OUT / "app" / served(rel))
shutil.rmtree(OUT / "app" / ".streamlit", ignore_errors=True)
file_map = {rel: {"url": f"./app/{served(rel)}"} for rel in files}
html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Gravity-Transition Readiness Model</title>
  <link rel="stylesheet" href="{STLITE}/stlite.css">
  <style>
    body {{ margin: 0; font-family: "IBM Plex Sans", system-ui, sans-serif; }}
    #loading {{ max-width: 34rem; margin: 18vh auto 0; padding: 0 1rem; color: #1B2A3A; text-align: center; }}
    #loading h1 {{ font-size: 1.5rem; margin: 0 0 .6rem; }}
    #loading p {{ color: #4A5568; line-height: 1.6; font-size: .95rem; }}
  </style>
</head>
<body>
  <div id="loading">
    <h1>Gravity-Transition Readiness Model</h1>
    <p>The model runs entirely in this browser. Loading Python and the model takes about 20–40 seconds on the first
    visit and is faster afterwards.</p>
    <p><a href="https://vishram0905.github.io/gravity-readiness-docs/">Documentation</a> ·
    <a href="https://github.com/vishram0905/gravity-readiness">Code</a></p>
  </div>
  <div id="root"></div>
  <script type="module">
    import {{ mount }} from "{STLITE}/stlite.js";
    mount({{
      requirements: ["numpy", "scipy", "pandas", "plotly"],
      entrypoint: "app.py",
      files: {json.dumps(file_map)},
    }}, document.getElementById("root"));
    const obs = new MutationObserver(() => {{
      if (document.body.innerText.includes("Model output")) {{ document.getElementById("loading").remove(); obs.disconnect(); }}
    }});
    obs.observe(document.body, {{ childList: true, subtree: true }});
  </script>
</body>
</html>
"""
(OUT / "index.html").write_text(html)
(OUT / ".nojekyll").write_text("")
print(len(files), "files")
