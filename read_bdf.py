
_charname = None
_bitmap = False

characters = {}

for line in open("terminus-font-4.48/ter-u32b.bdf", mode="rt"):
    line = line.strip()

    # look for control sequences
    if line.startswith("STARTCHAR"):
        if _charname:
            raise Exception("startchar before endchar")
        _charname = line.split(' ', 1)[1]
        characters[_charname] = []
        continue
    if line.startswith("BITMAP"):
        if not _charname:
            raise Exception("bitmap outside a char definition")
        _bitmap = True
        continue
    if line.startswith("ENDCHAR"):
        _charname = None
        _bitmap = False
        continue

    # look for data if in the correct state
    if _bitmap:
        characters[_charname].append(bytes.fromhex(line))
        continue

if __name__ == "__main__":
    print(characters.keys())
