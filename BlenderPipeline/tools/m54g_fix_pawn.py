# m54g_fix_pawn.py - M5.4f kok neden onarimi (D-098 hazirlik)
# Teshis (m54f v2 HEARTBEAT): PIE'de pawn=DefaultPawn_0 -> GameMode dogru ama
# default_pawn_class runtime'a gecmemis (CDO'ya yazildi, Blueprint defaults'a islenmedi).
# Onarim 1: CDO set -> compile -> tekrar set -> save (kalicilik).
# Onarim 2 (kursun gecirmez): haritaya BP_AF_VehiclePawn yerlestir, AutoPossess=Player0,
#            haritayi kaydet. Yerlestirilmis pawn'i controller dogrudan possess eder.
import unreal

TAG = "[M54G]"
RESULTS = []

def log(s):
    unreal.log(f"{TAG} {s}")

def check(name, ok, info=""):
    RESULTS.append((name, bool(ok)))
    log(f"{name} {'PASS' if ok else 'FAIL'}  {info}")

PAWN_PATH = "/Game/vehicle/BP_AF_VehiclePawn"
GM_PATH   = "/Game/vehicle/BP_AF_GameMode"
MAP_PATH  = "/Game/vehicle/Map_AF_DriveTest"

pawn_cls = unreal.load_object(None, PAWN_PATH + ".BP_AF_VehiclePawn_C")
check("PAWN-CLASS", pawn_cls is not None, str(pawn_cls))

# ---- Onarim 1: GameMode default_pawn_class kalici yap ----
try:
    bp  = unreal.EditorAssetLibrary.load_asset(GM_PATH)
    gen = unreal.BlueprintEditorLibrary.generated_class(bp)
    cdo = unreal.get_default_object(gen)
    log(f"GM oncesi default_pawn_class = {cdo.get_editor_property('default_pawn_class')}")
    cdo.set_editor_property("default_pawn_class", pawn_cls)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        log("GM compile edildi")
    except Exception as e:
        log(f"GM compile uyarisi: {e}")
    # compile CDO'yu sifirlayabilir -> tekrar set + save
    gen = unreal.BlueprintEditorLibrary.generated_class(bp)
    cdo = unreal.get_default_object(gen)
    cdo.set_editor_property("default_pawn_class", pawn_cls)
    unreal.EditorAssetLibrary.save_asset(GM_PATH)
    after = unreal.get_default_object(
        unreal.BlueprintEditorLibrary.generated_class(
            unreal.EditorAssetLibrary.load_asset(GM_PATH))).get_editor_property("default_pawn_class")
    check("GM-PAWN", after == pawn_cls, f"sonrasi={after}")
except Exception as e:
    check("GM-PAWN", False, f"hata: {e}")

# ---- Onarim 2: haritaya arac yerlestir + AutoPossess Player0 ----
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP_PATH)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # eski kopyalari temizle (idempotent)
    for a in list(actors.get_all_level_actors()):
        try:
            if a.get_class().get_name() == "BP_AF_VehiclePawn_C":
                actors.destroy_actor(a)
                log(f"eski arac silindi: {a.get_name()}")
        except Exception:
            pass
    veh = actors.spawn_actor_from_class(pawn_cls, unreal.Vector(0, 0, 150), unreal.Rotator(0, 0, 0))
    check("VEH-SPAWN", veh is not None, str(veh))
    veh.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
    ap = str(veh.get_editor_property("auto_possess_player"))
    check("AUTOPOSSESS", "PLAYER0" in ap.upper(), ap)
    saved = les.save_current_level()
    check("MAP-SAVE", bool(saved), f"saved={saved}")
except Exception as e:
    check("MAP-SAVE", False, f"hata: {e}")

log("===== OTOMATIK KONTROL =====")
for name, ok in RESULTS:
    log(f"{name:12}: {'PASS' if ok else 'FAIL'}")
overall = all(ok for _, ok in RESULTS)
log(f"SONUC {'PASS - simdi m54f_drive_test.py calistir + Play' if overall else 'FAIL - ciktiyi rapor et'}")
