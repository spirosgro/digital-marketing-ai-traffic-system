from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    "README.md", "LICENSE.md", "LICENSE-CODE", "CITATION.cff", "SECURITY.md",
    "data/synthetic-campaign-performance.csv", "output/channel-kpis.csv",
    "output/budget-recommendations.csv", "report/digital-marketing-ai-traffic-system.pdf",
    "presentation/digital-marketing-ai-traffic-system.pdf",
]
missing = [item for item in required if not (ROOT / item).is_file()]
if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))

forbidden = ["321/202", "@metis", "intelligence@", "Σπυρίδων", "Ιωακείμ"]
checked = [
    path for path in ROOT.rglob("*")
    if path.is_file()
    and path.suffix.lower() in {".md", ".csv", ".json", ".py", ".cff"}
    and path.name != "validate_repo.py"
]
findings = []
for path in checked:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for token in forbidden:
        if token.lower() in text.lower():
            findings.append(f"{path.relative_to(ROOT)}: {token}")
if findings:
    raise SystemExit("Potential private-source residue: " + "; ".join(findings))
print(f"Validated {len(checked)} public text files.")
