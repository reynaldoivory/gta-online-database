import pandas as pd
from pathlib import Path

SRC = Path("data/gta_vehicles_complete.csv")
DST = Path("data/gta_vehicles_complete.xlsx")

def main():
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")
    df = pd.read_csv(SRC)
    DST.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(DST, index=False)
    print(f"Wrote {DST} with {len(df)} rows and {len(df.columns)} columns")

if __name__ == "__main__":
    main()
