import sys

path = sys.argv[1]
verts = []
faces = 0
groups = {}
current = "(none)"

for line in open(path):
    parts = line.split()
    if not parts:
        continue
    if parts[0] == "v":
        verts.append(tuple(float(x) for x in parts[1:4]))
    elif parts[0] == "f":
        faces += 1
        groups[current] = groups.get(current, 0) + 1
    elif parts[0] in ("g", "o"):
        current = parts[1] if len(parts) > 1 else "(unnamed)"

xs = [v[0] for v in verts]
ys = [v[1] for v in verts]
zs = [v[2] for v in verts]

print("file             :", path)
print("vertices         :", len(verts))
print("faces            :", faces)
print("named groups     :", len(groups))
print("extent X (length): %f  [%f .. %f]" % (max(xs)-min(xs), min(xs), max(xs)))
print("extent Y (width) : %f  [%f .. %f]" % (max(ys)-min(ys), min(ys), max(ys)))
print("extent Z (height): %f  [%f .. %f]" % (max(zs)-min(zs), min(zs), max(zs)))
print("groups:")
for name, n in groups.items():
    print("  %-28s %d faces" % (name, n))
