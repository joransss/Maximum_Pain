"""Gun skin palettes for Maximum Pain (the menu plan's Phase F).

Every gun in the place is coloured from one 4 x 4 palette texture (16 colour squares; the M107 has its
own copy), and the guns' UVs only point at those squares. A skin's finish is a new palette in the same
layout: a colour map, a metalness map and a roughness map, each 256 x 256 (64-pixel squares), worked
out square by square from FINISHES below. Roblox shows them through a SurfaceAppearance per finish
(ReplicatedStorage.Assets.Skins.<finish>), which the game clones onto a gun's parts.

What each square colours was found on 2026-11-22 with two probe palettes (one coloured by column, one
by row) on all 13 guns; GROUPS names each square by that. A finish gives every group its colour, metal
and roughness; the squares that aren't the gun's body (markings, brass, shell red, the scope lens)
keep the original colours unless a finish says otherwise.

Pure Python (no Blender, no PIL): run it with Blender's bundled Python or any Python 3:
    D:\\5.2\\python\\bin\\python.exe -I skin_lib.py            (writes every finish)
    D:\\5.2\\python\\bin\\python.exe -I skin_lib.py chrome nickel   (only those)
It writes Exports/SKIN_<finish>_Color.png, _Metal.png and _Rough.png and Exports/manifest.json (each
file's size and SHA-256; identical maps are uploaded once). The same input always gives byte-identical
files. Uploaded ids go in Exports/skin_ids.json (by file name, with the SHA-256 they were uploaded for).

Uploading (from Studio, signed in as the place's owner, since an image only loads in places its owner
can use):
    D:\\5.2\\python\\bin\\python.exe -I skin_lib.py pending
        lists one file per image that has no id yet (a map changed since its upload counts as new);
    serve Exports on 127.0.0.1 (python -m http.server) and upload those files with Studio's MCP
        upload_image, saving its result ({"http://.../<file>": "rbxassetid://<id>"}) as JSON;
    D:\\5.2\\python\\bin\\python.exe -I skin_lib.py record <result.json>
        merges the result into skin_ids.json straight away (before the maps are made again), giving
        every file with the same image the same id.
Then each finish's SurfaceAppearance in ReplicatedStorage.Assets.Skins takes its three ids.
"""

import hashlib
import json
import os
import struct
import sys
import zlib

SIZE = 256
SQUARE = SIZE // 4
HERE = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(HERE, "Exports")

# What each square of the palette colours, by row (top first) and column (left first), as the probes
# showed it. "accent" is the top-left square: no large part uses it, so finishes treat it as dark metal.
GROUPS = [
    ["accent", "grip", "grip_wood", "marking"],
    ["brass", "shell", "body_paint", "lens"],
    ["polymer", "wood", "wood_dark", "metal_bright"],
    ["metal_dark", "metal", "metal_light", "metal_bright2"],
]

# The original palette (sampled from the texture, 2026-11-22), for the squares a finish keeps.
ORIGINAL = [
    ["#DF672A", "#151515", "#6E2C1C", "#E8E8E8"],
    ["#C99B3D", "#A3291E", "#8C7857", "#2D6F8F"],
    ["#2C2D31", "#8A4A24", "#5B3119", "#B3B8BE"],
    ["#27282C", "#3A3F45", "#59606A", "#8C939D"],
]

# Kept as they are by every finish unless it names them: (colour, metalness, roughness).
KEPT = {
    "marking": ("#E8E8E8", 0.0, 0.5),
    "brass": ("#C99B3D", 1.0, 0.35),
    "shell": ("#A3291E", 0.0, 0.6),
    "lens": ("#2D6F8F", 0.2, 0.05),
}


def paint(color, metal, rough, **overrides):
    """A finish where every metal square, the polymer and the painted body share one paint, shaded
    from dark to bright so the gun's details still read. `overrides` set any group outright."""
    groups = {}
    for group, shade in (
        ("metal_dark", 0.62),
        ("accent", 0.62),
        ("metal", 1.0),
        ("metal_light", 1.12),
        ("metal_bright2", 1.2),
        ("metal_bright", 1.27),
        ("body_paint", 1.0),
        ("polymer", 0.82),
    ):
        groups[group] = (shaded(color, shade), metal, rough)
    groups.update(overrides)
    return groups


def shaded(color, factor):
    r, g, b = parse(color)
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(channel * factor))) for channel in (r, g, b))


def parse(color):
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


WALNUT = {"wood": ("#6A3A1E", 0.0, 0.45), "wood_dark": ("#4E2A16", 0.0, 0.45), "grip_wood": ("#4E2A16", 0.0, 0.45)}
BLACK_GRIPS = {"grip": ("#121213", 0.0, 0.85)}

# Every finish: group -> (colour, metalness 0-1, roughness 0-1). Real gun finishes only (the vault's
# Gun Skin Ideas: no glow, no cartoon colours). Gold on its own is a mastery finish (never sold), so it
# only appears here as the second finish of BLACK AND GOLD.
FINISHES = {
    # GUNSMITH: realistic metal finishes.
    "parkerized": paint(
        "#3F433B", 0.35, 0.78,
        polymer=("#2B2C29", 0.0, 0.85), grip=("#161716", 0.0, 0.9),
        wood=("#6B4A2E", 0.0, 0.7), wood_dark=("#4A3220", 0.0, 0.7), grip_wood=("#4A3220", 0.0, 0.7),
    ),
    "sniper_grey": paint(
        "#5E6264", 0.05, 0.68,
        grip=("#1E2021", 0.0, 0.85),
        wood=("#5E6264", 0.05, 0.7), wood_dark=("#4F5355", 0.05, 0.7), grip_wood=("#1E2021", 0.0, 0.85),
    ),
    "od_green": paint(
        "#4A5236", 0.05, 0.7,
        grip=("#1C1F16", 0.0, 0.85),
        wood=("#4A5236", 0.05, 0.7), wood_dark=("#3E452D", 0.05, 0.72), grip_wood=("#1C1F16", 0.0, 0.85),
    ),
    "flat_dark_earth": paint(
        "#7A684D", 0.05, 0.72,
        metal_dark=("#2C2723", 0.1, 0.7), accent=("#2C2723", 0.1, 0.7), grip=("#2A2520", 0.0, 0.85),
        wood=("#7A684D", 0.05, 0.72), wood_dark=("#6E5D44", 0.05, 0.72), grip_wood=("#2A2520", 0.0, 0.85),
    ),
    # Bronze metal with black furniture: bronze over walnut read as one brown (checked in game).
    "burnt_bronze": paint(
        "#6E5034", 0.7, 0.45,
        polymer=("#1E1C1A", 0.0, 0.8), **BLACK_GRIPS,
        wood=("#1E1C1A", 0.0, 0.75), wood_dark=("#171615", 0.0, 0.75), grip_wood=("#171615", 0.0, 0.8),
    ),
    "blued_steel": paint(
        "#1E2531", 0.95, 0.25,
        polymer=("#16171A", 0.0, 0.75), grip=("#0F0F10", 0.0, 0.85), **WALNUT,
    ),
    "stainless": paint(
        "#9DA2A8", 0.95, 0.42,
        polymer=("#1E1F22", 0.0, 0.8), **BLACK_GRIPS, **WALNUT,
    ),
    "nickel": paint(
        "#A9A59B", 1.0, 0.18,
        polymer=("#1A1A1B", 0.0, 0.75), **BLACK_GRIPS, **WALNUT,
    ),
    "royal_blue": paint(
        "#1A2C5E", 1.0, 0.08,
        polymer=("#121318", 0.0, 0.7), grip=("#5E3219", 0.0, 0.35),
        wood=("#6A3A1E", 0.0, 0.35), wood_dark=("#4E2A16", 0.0, 0.35), grip_wood=("#5E3219", 0.0, 0.35),
    ),
    # STREET: paint jobs.
    "urban": paint(
        "#4D535B", 0.05, 0.68,
        polymer=("#2B3647", 0.0, 0.72), grip=("#181B20", 0.0, 0.85),
        wood=("#4D535B", 0.05, 0.7), wood_dark=("#2B3647", 0.0, 0.72), grip_wood=("#181B20", 0.0, 0.85),
    ),
    "midnight": paint(
        "#17181A", 0.3, 0.62,
        polymer=("#121314", 0.0, 0.75), grip=("#0B0B0C", 0.0, 0.85),
        wood=("#17181A", 0.0, 0.7), wood_dark=("#121314", 0.0, 0.72), grip_wood=("#0B0B0C", 0.0, 0.85),
    ),
    "desert": paint(
        "#B59A6A", 0.05, 0.72,
        metal_dark=("#6B5A3E", 0.05, 0.75), accent=("#6B5A3E", 0.05, 0.75),
        polymer=("#8E7550", 0.0, 0.75), grip=("#4A3D2B", 0.0, 0.85),
        wood=("#8E7550", 0.0, 0.75), wood_dark=("#7A6444", 0.0, 0.75), grip_wood=("#4A3D2B", 0.0, 0.85),
    ),
    "woodland": paint(
        "#4C5A2E", 0.05, 0.72,
        metal_dark=("#262B1E", 0.05, 0.75), accent=("#262B1E", 0.05, 0.75),
        metal_light=("#5C4630", 0.05, 0.72), metal_bright2=("#3A4A28", 0.05, 0.72), metal_bright=("#6B7A3E", 0.05, 0.72),
        polymer=("#3A2E22", 0.0, 0.75), grip=("#1C1F16", 0.0, 0.85),
        wood=("#5C4630", 0.0, 0.75), wood_dark=("#3A2E22", 0.0, 0.75), grip_wood=("#1C1F16", 0.0, 0.85),
    ),
    "rust": paint(
        "#7A3E1E", 0.25, 0.88,
        metal_dark=("#3A2216", 0.2, 0.9), accent=("#3A2216", 0.2, 0.9),
        polymer=("#2E2A27", 0.0, 0.9), grip=("#1E1B19", 0.0, 0.92),
        wood=("#6E6458", 0.0, 0.9), wood_dark=("#5A5248", 0.0, 0.9), grip_wood=("#4A4038", 0.0, 0.9),
    ),
    "arctic": paint(
        "#B9BDC1", 0.05, 0.66,
        metal_dark=("#6E7377", 0.05, 0.7), accent=("#6E7377", 0.05, 0.7),
        polymer=("#A9AEB2", 0.0, 0.7), grip=("#4A4E52", 0.0, 0.8),
        wood=("#C9CDD0", 0.0, 0.7), wood_dark=("#A9AEB2", 0.0, 0.7), grip_wood=("#4A4E52", 0.0, 0.8),
    ),
    # CARTEL: plating and luxury.
    # Ebony furniture: copper over walnut read as one orange-brown (checked in game).
    "copper": paint(
        "#9A5A36", 1.0, 0.28,
        polymer=("#1A1A1B", 0.0, 0.75), **BLACK_GRIPS,
        wood=("#1F1714", 0.0, 0.4), wood_dark=("#191311", 0.0, 0.4), grip_wood=("#191311", 0.0, 0.4),
    ),
    "champagne": paint(
        "#B8A985", 1.0, 0.3,
        polymer=("#1C1B19", 0.0, 0.75), grip=("#141312", 0.0, 0.85),
        wood=("#5E3A22", 0.0, 0.45), wood_dark=("#4A2C18", 0.0, 0.45), grip_wood=("#4A2C18", 0.0, 0.45),
    ),
    "chrome": paint(
        "#C4C8CD", 1.0, 0.04,
        polymer=("#141516", 0.0, 0.6), grip=("#0E0E0F", 0.0, 0.7),
        wood=("#5E3219", 0.0, 0.35), wood_dark=("#4A2614", 0.0, 0.35), grip_wood=("#4A2614", 0.0, 0.35),
    ),
    "rose_gold": paint(
        "#B07A68", 1.0, 0.16,
        polymer=("#18161A", 0.0, 0.7), grip=("#100E10", 0.0, 0.8),
        wood=("#4A2614", 0.0, 0.4), wood_dark=("#3A1E10", 0.0, 0.4), grip_wood=("#3A1E10", 0.0, 0.4),
    ),
    "black_chrome": paint(
        "#1C1C1F", 1.0, 0.08,
        polymer=("#121213", 0.0, 0.6), grip=("#0B0B0C", 0.0, 0.7),
        wood=("#1C1C1F", 1.0, 0.08), wood_dark=("#121213", 0.0, 0.6), grip_wood=("#0B0B0C", 0.0, 0.7),
    ),
    # A deeper gold: #C9A13A's bright squares clipped to lemon yellow, #A88A30's main squares read as
    # mustard (both checked in game).
    "gold": paint(
        "#B08E30", 1.0, 0.14,
        polymer=("#141414", 0.0, 0.7), **BLACK_GRIPS, **WALNUT,
    ),
    "ivory_gold": paint(
        "#B08E30", 1.0, 0.14,
        polymer=("#E5DCC5", 0.0, 0.35), grip=("#E5DCC5", 0.0, 0.35),
        wood=("#E5DCC5", 0.0, 0.35), wood_dark=("#D8CEB4", 0.0, 0.35), grip_wood=("#D8CEB4", 0.0, 0.35),
    ),
}


def squares(finish):
    """The finish's 16 squares, row by row: (colour, metalness, roughness)."""
    out = []
    for row in range(4):
        cells = []
        for column in range(4):
            group = GROUPS[row][column]
            if group in finish:
                cells.append(finish[group])
            elif group in KEPT:
                cells.append(KEPT[group])
            else:
                raise ValueError("a finish is missing group " + group)
        out.append(cells)
    return out


def png(rows, grey=False):
    """An 8-bit PNG (RGB, or greyscale), no metadata, so the same pixels give the same bytes."""
    width = len(rows[0]) // (1 if grey else 3)
    raw = b"".join(b"\x00" + bytes(row) for row in rows)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, len(rows), 8, 0 if grey else 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def maps(name):
    cells = squares(FINISHES[name])
    color, metal, rough = [], [], []
    for y in range(SIZE):
        crow, mrow, rrow = [], [], []
        for x in range(SIZE):
            hexcolor, metalness, roughness = cells[y // SQUARE][x // SQUARE]
            crow.extend(parse(hexcolor))
            mrow.append(round(metalness * 255))
            rrow.append(round(roughness * 255))
        color.append(crow)
        metal.append(mrow)
        rough.append(rrow)
    return {"Color": png(color), "Metal": png(metal, grey=True), "Rough": png(rough, grey=True)}


def check():
    for name, finish in FINISHES.items():
        for group, (color, metalness, roughness) in finish.items():
            assert len(color) == 7 and color[0] == "#", (name, group)
            assert 0 <= metalness <= 1 and 0 <= roughness <= 1, (name, group)
        squares(finish)  # every group present


def load_ids():
    path = os.path.join(EXPORTS, "skin_ids.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ids(ids):
    with open(os.path.join(EXPORTS, "skin_ids.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(sorted(ids.items())), f, indent=2)
        f.write("\n")


def pending():
    """The files still to upload: one per distinct image (by SHA-256) that has no id yet."""
    with open(os.path.join(EXPORTS, "manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f)
    uploaded = {entry["sha256"] for entry in load_ids().values()}
    seen = set()
    for file_name, entry in sorted(manifest.items()):
        if entry["sha256"] not in uploaded and entry["sha256"] not in seen:
            seen.add(entry["sha256"])
            print(file_name)


def record(result_path):
    """Merges an upload's result ({"http://.../<file>": "rbxassetid://<id>"}) into skin_ids.json, and
    gives every file with the same image the same id."""
    with open(os.path.join(EXPORTS, "manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(result_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    # Run it straight after the upload, before the maps are made again: a result's file names are
    # matched to their images through the manifest as it is now.
    by_hash = {entry["sha256"]: entry["id"] for entry in load_ids().values()}
    for url, content in result.items():
        file_name = url.rsplit("/", 1)[-1]
        by_hash[manifest[file_name]["sha256"]] = int(content.rsplit("//", 1)[-1])
    # Only the files as they are now: one whose image changed has no id until it is uploaded again.
    ids = {}
    for file_name, entry in manifest.items():
        if entry["sha256"] in by_hash:
            ids[file_name] = {"sha256": entry["sha256"], "id": by_hash[entry["sha256"]]}
    save_ids(ids)
    print("ids for", len(ids), "of", len(manifest), "files")


def main(names):
    if names[:1] == ["pending"]:
        pending()
        return
    if names[:1] == ["record"]:
        record(names[1])
        return
    check()
    os.makedirs(EXPORTS, exist_ok=True)
    manifest_path = os.path.join(EXPORTS, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    for name in names or sorted(FINISHES):
        if name not in FINISHES:
            raise SystemExit("no finish called " + name)
        for kind, data in maps(name).items():
            file_name = "SKIN_%s_%s.png" % (name, kind)
            with open(os.path.join(EXPORTS, file_name), "wb") as f:
                f.write(data)
            manifest[file_name] = {"finish": name, "map": kind, "width": SIZE, "height": SIZE, "sha256": hashlib.sha256(data).hexdigest()}
            print("wrote", file_name)
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(sorted(manifest.items())), f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
