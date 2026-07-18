#!/usr/bin/env python3
"""Repair corrupted boolean columns in data/gta_vehicles_complete.csv.

Background
----------
The original scraper matched feature keywords ("weaponized", "HSW", "arena")
against whole-page text -- including site navigation -- so every row ended up
Weaponized=TRUE, 758/795 rows HSW=TRUE, and 135 rows Arena=TRUE (the real
Arena War roster is ~49 rows in this dataset). This script recomputes the
three corrupted columns (Weaponized, HSW, Arena) from authoritative name
lists embedded below. The Imani and Bennys columns are left untouched.

Both copies of the CSV are rewritten identically:
  - data/gta_vehicles_complete.csv
  - GTA-Vehicle-Database-App/public/gta_vehicles_complete.csv

Sources (fetched 2026-07-18)
----------------------------
WEAPONIZED (99 entries, verbatim):
  https://www.gtabase.com/grand-theft-auto-v/guides/list-of-vehicles-in-gta-5-gta-online-by-feature?feature=weaponized
  Spot-verified against individual GTABase vehicle pages (e.g. Annis Savestra
  and Pfister Comet Safari both list "Weaponized Vehicle" + Mounted Machine
  Guns -- they are Arena War drip-feed cars with weapon options).
HSW (30 entries, verbatim):
  https://www.gtabase.com/grand-theft-auto-v/guides/list-of-vehicles-in-gta-5-gta-online-by-feature?feature=hsw
  Note: "FMJ MK V" is a separate paid conversion of the FMJ (confirmed on
  https://www.gtabase.com/grand-theft-auto-v/vehicles/vapid-fmj : "Variant /
  Conversion: FMJ MK V - $2,965,000"); the plain FMJ has NO HSW, so the FMJ
  row correctly stays FALSE.
ARENA (12 Arena Contender base vehicles):
  https://www.gtabase.com/grand-theft-auto-v/guides/list-of-vehicles-in-gta-5-gta-online-by-feature?feature=arena-war
  In-game each contender exists as Apocalypse / Future Shock / Nightmare
  variants; this CSV carries all three variant rows plus a base
  "<Name> (Arena)" row per contender. The RC Bandito (Arena War DLC, Arena
  Workshop vehicle) is also flagged. All Arena vehicles are weaponized
  (mines / rocket boost / weapon mods), so Arena=TRUE implies
  Weaponized=TRUE. The 12 contender base names that appear on the GTABase
  weaponized list refer to those Arena versions, not the identically named
  regular cars (Dominator, Impaler, Issi, Slamvan, ...), so they are matched
  through the Arena rule rather than by bare name.

Usage
-----
    python3 scripts/fix_boolean_flags.py            # repair + report
    python3 scripts/fix_boolean_flags.py --dry-run  # report only, no writes
"""

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CSV_PATHS = [
    REPO / "data" / "gta_vehicles_complete.csv",
    REPO / "GTA-Vehicle-Database-App" / "public" / "gta_vehicles_complete.csv",
]
ORACLE_PATH = REPO / "data" / "final_database.csv"

# --------------------------------------------------------------------------
# Authoritative lists ("Make | Model", verbatim from the sources above)
# --------------------------------------------------------------------------

WEAPONIZED = [
    "Nagasaki | Akula",
    "Western Company | Annihilator",
    "Western Company | Annihilator Stealth",
    "Vom Feuer | Anti-Aircraft Trailer",
    "HVY | APC Tank",
    "Ocelot | Ardent",
    "Brute | Armored Boxville",
    "Mammoth | Avenger",
    "LCC | B-11 Strikeforce",
    "HVY | Barrage",
    "Nagasaki | Blazer Aqua",
    "Benefactor | Bruiser",  # Arena Contender -- matched via Arena rule
    "Declasse | Brutus",  # Arena Contender -- matched via Arena rule
    "Bravado | Buffalo STX",
    "Nagasaki | Buzzard Attack Chopper",
    "Vapid | Caracara",
    "Vapid | Caracara Armored",
    "MTL | Cerberus",  # Arena Contender -- matched via Arena rule
    "Dewbauchee | Champion",
    "HVY | Chernobog",
    "Pfister | Comet Safari",
    "Western | Deathbike",  # Arena Contender -- matched via Arena rule
    "Enus | Deity",
    "Imponte | Deluxo",
    "Vapid | Dominator",  # Arena Contender -- matched via Arena rule
    "BF | Dune FAV",
    "Western Company | Duster 300-H",
    "Mammoth | F-160 Raiju",
    "FH-1 | Hunter",
    "MTL | Fire Truck",
    "Declasse | Granger 3600LX",
    "Bravado | Half-track",
    "Nagasaki | Havok",
    "Mammoth | Hydra",
    "Declasse | Impaler",  # Arena Contender -- matched via Arena rule
    "Vapid | Imperator",  # Arena Contender -- matched via Arena rule
    "HVY | Insurgent Pick-up",
    "HVY | Insurgent Pick-up Custom",
    "Invade and Persuade | RC Tank",
    "Weeny | Issi",  # Arena Contender -- matched via Arena rule
    "Dewbauchee | JB 700W",
    "Enus | Jubilee",
    "RUNE | Kosatka",
    "Kurtz | 31 Patrol Boat",
    "LCC | LF-22 Starling",
    "HVY | Menacer",
    "Mobile Operations | Center Trailer",
    "Mammoth | Mogul",
    "Maibatsu | Mule Custom",
    "HVY | Nightshark",
    "Pegassi | Oppressor",
    "Pegassi | Oppressor Mk II",
    "P-45 | Nokota",
    "JoBuilt | P-996 LAZER",
    "Enus | Paragon R Armored",
    "Mammoth | Patriot Mil-Spec",
    "MTL | Pounder Custom",
    "Buckingham | Pyro",
    "RC | Bandito",  # Arena Workshop vehicle -- matched via Arena rule
    "RCV | RCV",
    "Übermacht | Revolter",
    "Rhino | Tank",
    "RM-10 | Bombushka",
    "RO-86 | Alkonost",
    "Western Company | Rogue",
    "Imponte | Ruiner 2000",
    "Bravado | Sasquatch",  # Arena Contender -- matched via Arena rule
    "Savage | Savage",
    "Annis | Savestra",
    "HVY | Scarab",  # Arena Contender -- matched via Arena rule
    "Declasse | Scramjet",
    "Sea | Sparrow",
    "Western Company | Seabreeze",
    "Vapid | Slamvan",  # Arena Contender -- matched via Arena rule
    "Sparrow | Sparrow",
    "Vapid | Speedo Custom",
    "Mammoth | Streamer216",
    "Ocelot | Stromberg",
    "Karin | Technical",
    "Karin | Technical Aqua",
    "Karin | Technical Custom",
    "Benefactor | Terrorbyte",
    "Mammoth | Thruster Jetpack",
    "Eberhard | Titan 250 D",
    "TM-02 | Khanjali Tank",
    "Pegassi | Toreador",
    "Mammoth | Tula",
    "Benefactor | Turreted Limo",
    "Nagasaki | Ultralight",
    "V-65 | Molotok",
    "Buckingham | Valkyrie",
    "Grotti | Vigilante",
    "Lampadati | Viseris",
    "Volatol | Volatol",
    "Buckingham | Weaponized Conada",
    "Nagasaki | Weaponized Dinghy",
    "Pegassi | Weaponized Ignus",
    "Declasse | Weaponized Tampa",
    "Annis | ZR380",  # Arena Contender -- matched via Arena rule
]

HSW = [
    "Bravado | Banshee GTS",
    "Grotti | Stinger TT",
    "Declasse | Tampa GT",
    "Grotti | Veleno GT",
    "Übermacht | Niobe",
    "Declasse | Vigero ZX",
    "Declasse | Vigero ZX Convertible",
    "Shitzu | Hakuchou Drag Bike",
    "Karin | S95",
    "Benefactor | Stirling GT",
    "Vapid | FMJ MK V",  # separate conversion; plain FMJ has no HSW
    "Bravado | Banshee",
    "Grotti | Turismo Classic",
    "Overflod | Entity MT",
    "Principe | Deveste Eight",
    "Pfister | Astrale",
    "Pegassi | Weaponized Ignus",
    "Bravado | Buffalo EVX",
    "Penaud | La Coureuse",
    "Imponte | Arbiter GT",
    "Coil | Cyclone II",
    "Vapid | Firebolt ASP",
    "Weeny | Issi Rally",
    "Übermacht | Sentinel XS",
    "Karin | Woodlander",
    "Pfister | Astron Custom",
    "Maibatsu | MonstroCiti",
    "Grotti | Brioso R/A",
    "Annis | Euros X32",
    "Karin | Vivanite",
]

# The 12 Arena Contender base vehicles (GTABase feature=arena-war).
ARENA_CONTENDERS = [
    "Benefactor | Bruiser",
    "Declasse | Brutus",
    "MTL | Cerberus",
    "Western | Deathbike",
    "Vapid | Dominator",
    "Declasse | Impaler",
    "Vapid | Imperator",
    "Weeny | Issi",
    "Bravado | Sasquatch",
    "HVY | Scarab",
    "Vapid | Slamvan",
    "Annis | ZR380",
]
ARENA_VARIANT_PREFIXES = ["Apocalypse", "Future Shock", "Nightmare"]

# --------------------------------------------------------------------------
# Name normalization / matching
# --------------------------------------------------------------------------


def norm(s: str) -> str:
    """lowercase, unify Mk-Roman-numeral spellings, strip non-alphanumerics."""
    s = s.lower()
    s = re.sub(r"\bmk\.?\s*iii\b", "mk3", s)
    s = re.sub(r"\bmk\.?\s*ii\b", "mk2", s)
    s = re.sub(r"\bmk\.?\s*i\b", "mk1", s)
    return re.sub(r"[^a-z0-9]", "", s)


def _dedup_tokens(make: str, model: str) -> str:
    """Join make+model, collapsing consecutive duplicate words.

    Handles CSV make/model split artifacts such as
    ('Western Company', 'Company Rogue') -> 'western company rogue' and
    ('Vom Feuer', 'Feuer Anti-Aircraft Trailer'), ('Akula', 'Akula').
    """
    out = []
    for tok in f"{make} {model}".split():
        key = re.sub(r"[^a-z0-9]", "", tok.lower())
        if out and key == out[-1][0]:
            continue
        out.append((key, tok))
    return " ".join(t for _, t in out)


def keys_for(make: str, model: str) -> set:
    """All normalized keys under which an entry can match."""
    ks = {norm(model), norm(_dedup_tokens(make, model))}
    # Fallback: parenthetical qualifiers like "(Submarine HQ)" -- but never
    # strip "(Arena)", which distinguishes Arena vehicles from regular ones.
    paren = re.search(r"\(([^)]*)\)", model)
    if paren and "arena" not in paren.group(1).lower():
        stripped = re.sub(r"\([^)]*\)", " ", model)
        ks.add(norm(stripped))
        ks.add(norm(_dedup_tokens(make, stripped)))
    ks.discard("")
    return ks


def parse_entry(entry: str):
    make, _, model = entry.partition("|")
    return make.strip(), model.strip()


CONTENDER_BASES = {norm(parse_entry(e)[1]) for e in ARENA_CONTENDERS}


def is_arena(make: str, model: str) -> bool:
    nm = norm(model)
    # "Bruiser (Arena)" ... "ZR380 (Arena)" base rows
    if re.search(r"\(\s*arena\s*\)", model, re.I):
        base = norm(re.sub(r"\(\s*arena\s*\)", " ", model, flags=re.I))
        if base in CONTENDER_BASES:
            return True
    # "Apocalypse/Future Shock/Nightmare <Contender>" variant rows
    for prefix in ARENA_VARIANT_PREFIXES:
        p = norm(prefix)
        if nm.startswith(p) and nm[len(p):] in CONTENDER_BASES:
            return True
    # RC Bandito (Arena Workshop vehicle)
    if norm(_dedup_tokens(make, model)) == "rcbandito":
        return True
    return False


def build_index(entries, skip_contenders: bool):
    """Map normalized key -> source entry. Contender-named weaponized entries
    are matched via the Arena rule instead of by bare name (a bare 'Dominator'
    key would wrongly flag the regular Vapid Dominator muscle car)."""
    index = {}
    skipped = []
    for entry in entries:
        make, model = parse_entry(entry)
        if skip_contenders and norm(model) in CONTENDER_BASES:
            skipped.append(entry)
            continue
        for k in keys_for(make, model):
            index.setdefault(k, []).append(entry)
    return index, skipped


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def main(dry_run: bool) -> int:
    with open(CSV_PATHS[0], newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    col = {name: header.index(name) for name in header}
    weap_idx, skipped_contenders = build_index(WEAPONIZED, skip_contenders=True)
    hsw_idx, _ = build_index(HSW, skip_contenders=False)

    matched_entries = set()
    before = {c: sum(1 for r in rows if r[col[c]] == "TRUE")
              for c in ("Weaponized", "HSW", "Arena")}

    for r in rows:
        make, model = r[col["GTA_Make"]], r[col["GTA_Model"]]
        ks = keys_for(make, model)
        arena = is_arena(make, model)
        weap_hit = next((weap_idx[k] for k in ks if k in weap_idx), None)
        hsw_hit = next((hsw_idx[k] for k in ks if k in hsw_idx), None)
        for idx in (weap_idx, hsw_idx):
            for k in ks:
                matched_entries.update(idx.get(k, []))
        if arena:
            base = norm(re.sub(r"\(\s*arena\s*\)", " ", model, flags=re.I))
            for prefix in ARENA_VARIANT_PREFIXES:
                p = norm(prefix)
                if base.startswith(p):
                    base = base[len(p):]
            for entry in ARENA_CONTENDERS + ["RC | Bandito"]:
                if norm(parse_entry(entry)[1]) == base or (
                        base == "rcbandito" or norm(_dedup_tokens(make, model)) == "rcbandito"):
                    matched_entries.add(entry)
        r[col["Weaponized"]] = "TRUE" if (weap_hit or arena) else "FALSE"
        r[col["HSW"]] = "TRUE" if hsw_hit else "FALSE"
        r[col["Arena"]] = "TRUE" if arena else "FALSE"
        # Imani and Bennys intentionally untouched.

    after = {c: sum(1 for r in rows if r[col[c]] == "TRUE")
             for c in ("Weaponized", "HSW", "Arena")}

    print("TRUE counts (before -> after):")
    for c in ("Weaponized", "HSW", "Arena"):
        print(f"  {c:<10} {before[c]:>3} -> {after[c]}")

    # Web-list entries that matched no CSV row (do not silently drop them).
    print("\nSource entries with no matching CSV row:")
    unmatched = 0
    for label, entries in (("WEAPONIZED", WEAPONIZED), ("HSW", HSW),
                           ("ARENA", ARENA_CONTENDERS + ["RC | Bandito"])):
        for entry in entries:
            if entry not in matched_entries and entry not in skipped_contenders:
                print(f"  [{label}] {entry}")
                unmatched += 1
            elif entry in skipped_contenders and entry not in matched_entries:
                print(f"  [{label}] {entry} (Arena rule found no rows!)")
                unmatched += 1
    if not unmatched:
        print("  (none)")

    # Oracle spot-check against the hand-written 80-row final_database.csv.
    print("\nOracle comparison (data/final_database.csv, Yes/No columns):")
    disagreements = 0
    with open(ORACLE_PATH, newline="", encoding="utf-8") as f:
        oracle = list(csv.DictReader(f))
    row_by_key = {}
    for r in rows:
        for k in keys_for(r[col["GTA_Make"]], r[col["GTA_Model"]]):
            row_by_key.setdefault(k, r)
    for o in oracle:
        hit = next((row_by_key[k] for k in keys_for(o["Make"], o["Model"])
                    if k in row_by_key), None)
        if hit is None:
            print(f"  [no CSV row] {o['Make']} {o['Model']}")
            continue
        for ocol, ccol in (("Weaponized", "Weaponized"), ("HSW", "HSW")):
            want = "TRUE" if o[ocol].strip().lower() == "yes" else "FALSE"
            got = hit[col[ccol]]
            if want != got:
                disagreements += 1
                print(f"  [{ccol}] {o['Make']} {o['Model']}: "
                      f"oracle={o[ocol]} csv={got}")
    if not disagreements:
        print("  (no disagreements)")

    # Hard-coded sanity expectations.
    print("\nSanity checks:")
    checks = [
        ("Obey", "10F", "Weaponized", "FALSE"),
        ("Obey", "10F", "HSW", "FALSE"),
        ("Pegassi", "Oppressor Mk II", "Weaponized", "TRUE"),
        ("Imponte", "Deluxo", "Weaponized", "TRUE"),
        ("Declasse", "Vigero ZX", "HSW", "TRUE"),
    ]
    ok = True
    by_mm = {(r[col["GTA_Make"]], r[col["GTA_Model"]]): r for r in rows}
    for make, model, c, want in checks:
        r = by_mm.get((make, model))
        got = r[col[c]] if r else "<row missing>"
        status = "ok" if got == want else "FAIL"
        if got != want:
            ok = False
        print(f"  [{status}] {make} {model} {c}={got} (expected {want})")

    if dry_run:
        print("\n--dry-run: no files written.")
        return 0 if ok else 1

    import io
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    payload = buf.getvalue()
    for path in CSV_PATHS:
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write(payload)
        print(f"\nwrote {path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main("--dry-run" in sys.argv[1:]))
