# m54h_add_light.py - Map_AF_DriveTest'e isik ekler (simsiyah ekran onarimi).
# Neden: m54e haritaya sadece zemin + PlayerStart koydu; isik aktoru yok.
# Isiksiz haritada PIE goruntusu tamamen siyahtir - bu motor hatasi degil, eksik asset.
# Kosum: UE Output Log ->  py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/m54h_add_light.py"

import unreal

MAP_PATH = "/Game/vehicle/Map_AF_DriveTest"
results = []

def log(msg):
    unreal.log("[M54H] " + msg)

def add(name, ok, detail=""):
    results.append((name, ok, detail))
    log("%s %s  %s" % (name, "PASS" if ok else "FAIL", detail))

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level(MAP_PATH)
log("Harita yuklendi: %s" % MAP_PATH)

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()

def find(cls):
    for a in actors:
        if isinstance(a, cls):
            return a
    return None

# 1) DirectionalLight (gunes)
dl = find(unreal.DirectionalLight)
if not dl:
    rot = unreal.Rotator()
    rot.pitch = -45.0
    rot.yaw = 30.0
    dl = eas.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 500), rot)
try:
    dlc = dl.get_component_by_class(unreal.DirectionalLightComponent)
    dlc.set_intensity(8.0)
    add("DIRLIGHT", dl is not None, str(dl.get_name()) if dl else "-")
except Exception as e:
    add("DIRLIGHT", dl is not None, "spawn ok, intensity atlandi: %r" % e)

# 2) SkyLight (ortam isigi - golgeler tam siyah olmasin)
sl = find(unreal.SkyLight)
if not sl:
    sl = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 400), unreal.Rotator())
add("SKYLIGHT", sl is not None, str(sl.get_name()) if sl else "-")

# 3) SkyAtmosphere (gokyuzu gorseli; yoksa gok siyah kalir)
sa = find(unreal.SkyAtmosphere)
if not sa:
    sa = eas.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator())
add("SKYATMO", sa is not None, str(sa.get_name()) if sa else "-")

# 4) Kaydet
saved = les.save_current_level()
add("MAP-SAVE", bool(saved), "saved=%s" % saved)

log("===== OTOMATIK KONTROL =====")
all_ok = all(ok for _, ok, _ in results)
for name, ok, detail in results:
    log("%-9s : %s  (%s)" % (name, "PASS" if ok else "FAIL", detail))
log("SONUC %s - %s" % ("PASS" if all_ok else "FAIL",
    "isik tamam; simdi m54f_drive_test.py v3 calistir + Play" if all_ok
    else "FAIL satirini raporla"))
