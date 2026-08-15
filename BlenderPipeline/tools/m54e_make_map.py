# m54e_make_map.py - D-097 (M5.4e)
# BP_AF_GameMode (DefaultPawn=BP_AF_VehiclePawn) + Map_AF_DriveTest
# (duz zemin + PlayerStart + WorldSettings GameMode override)
# Idempotent: tekrar kosulursa mevcut assetleri kullanir/duzeltir.
import unreal

RESULTS = []
def check(tag, cond, detail=""):
    s = "PASS" if cond else "FAIL"
    RESULTS.append(cond)
    unreal.log("[M54E] {} {}  {}".format(tag, s, detail))

VEH_DIR  = "/Game/vehicle"
PAWN     = VEH_DIR + "/BP_AF_VehiclePawn"
GM_PATH  = VEH_DIR + "/BP_AF_GameMode"
MAP_PATH = VEH_DIR + "/Map_AF_DriveTest"

at  = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

# ---- 1) GameMode BP + DefaultPawnClass ----
gm_class = None
try:
    if not eal.does_asset_exist(GM_PATH):
        f = unreal.BlueprintFactory()
        f.set_editor_property("parent_class", unreal.GameModeBase)
        at.create_asset("BP_AF_GameMode", VEH_DIR, None, f)
    gm_class   = unreal.load_object(None, GM_PATH + ".BP_AF_GameMode_C")
    pawn_class = unreal.load_object(None, PAWN + ".BP_AF_VehiclePawn_C")
    check("GM-CLASS", gm_class is not None and pawn_class is not None,
          "gm={} pawn={}".format(gm_class, pawn_class))
    cdo = unreal.get_default_object(gm_class)
    cdo.set_editor_property("default_pawn_class", pawn_class)
    rb = cdo.get_editor_property("default_pawn_class")
    check("GM-PAWN", rb is not None and rb.get_name() == "BP_AF_VehiclePawn_C",
          "default_pawn_class=" + str(rb))
    eal.save_asset(GM_PATH)
except Exception as e:
    check("GM", False, repr(e))

# ---- 2) Level yarat/yukle ----
try:
    if eal.does_asset_exist(MAP_PATH):
        ok = les.load_level(MAP_PATH)
    else:
        ok = les.new_level(MAP_PATH)
    check("LEVEL", bool(ok), MAP_PATH)
except Exception as e:
    check("LEVEL", False, repr(e))

def find_actor(label):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None

# ---- 3) Zemin: 100x100 m kup plaka (ust yuzey z=0) ----
try:
    cube = unreal.load_asset("/Engine/BasicShapes/Cube")
    floor = find_actor("AF_Floor")
    if floor is None:
        floor = eas.spawn_actor_from_class(unreal.StaticMeshActor,
                                           unreal.Vector(0, 0, -50))
        floor.set_actor_label("AF_Floor")
    smc = floor.static_mesh_component
    smc.set_editor_property("static_mesh", cube)
    floor.set_actor_scale3d(unreal.Vector(100.0, 100.0, 1.0))
    floor.set_actor_location(unreal.Vector(0, 0, -50), False, False)
    check("FLOOR", smc.get_editor_property("static_mesh") is not None,
          "scale={} loc={}".format(floor.get_actor_scale3d(),
                                   floor.get_actor_location()))
except Exception as e:
    check("FLOOR", False, repr(e))

# ---- 4) PlayerStart (zemin ustunde 150 cm) ----
try:
    ps = find_actor("AF_PlayerStart")
    if ps is None:
        ps = eas.spawn_actor_from_class(unreal.PlayerStart,
                                        unreal.Vector(0, 0, 150))
        ps.set_actor_label("AF_PlayerStart")
    ps.set_actor_location(unreal.Vector(0, 0, 150), False, False)
    check("PSTART", ps is not None, "loc=" + str(ps.get_actor_location()))
except Exception as e:
    check("PSTART", False, repr(e))

# ---- 5) WorldSettings GameMode override ----
try:
    world = ues.get_editor_world()
    ws = unreal.GameplayStatics.get_actor_of_class(world, unreal.WorldSettings)
    ws.set_editor_property("default_game_mode", gm_class)
    rb = ws.get_editor_property("default_game_mode")
    check("GMODE-OVR", rb is not None and rb.get_name() == "BP_AF_GameMode_C",
          "world_settings.default_game_mode=" + str(rb))
except Exception as e:
    check("GMODE-OVR", False, repr(e))

# ---- 6) Kaydet ----
try:
    saved = les.save_current_level()
    check("SAVE", bool(saved) and eal.does_asset_exist(MAP_PATH),
          "map_exists={}".format(eal.does_asset_exist(MAP_PATH)))
except Exception as e:
    check("SAVE", False, repr(e))

unreal.log("===== OTOMATIK KONTROL =====")
unreal.log("[M54E] SONUC " + ("PASS - M5.4e tamam; M5.4f surus kabulune gec"
           if all(RESULTS) else "FAIL - yukaridaki FAIL satirlarini yapistir"))
