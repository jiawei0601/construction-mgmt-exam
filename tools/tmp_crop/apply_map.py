import json, shutil, sys, os
map_path = sys.argv[1]
with open(map_path, "r", encoding="utf-8") as f:
    pairs = json.load(f)
for src, dst in pairs:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    print("OK", src, "->", dst)
