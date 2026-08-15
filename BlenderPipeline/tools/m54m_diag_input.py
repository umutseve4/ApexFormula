# m54m_diag_input.py - Deneme #6 TESHIS: Enhanced Input zinciri PIE'de gercekten kurulu mu?
# KULLANIM: UE'de Play'e bas (PIE calisirken), sonra Output Log'a:
#   py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/m54m_diag_input.py"
# Script HICBIR seyi kalici degistirmez; sadece olcer ve IMC eksikse RUNTIME'a ekler.
# IMC eklendikten sonra HEMEN viewport'a tiklayip W'ye bas: arac hareket ederse kok neden = kayit (registration).
import unreal

TAG = "[M54M]"
R = []
def log(name, ok, info=""):
    s = "PASS" if ok else "FAIL"
    R.append((name, s, str(info)))
    unreal.log(f"{TAG} {name} {s}  {info}")

def keyname(k):
    try:
        return str(k.get_editor_property("key_name"))
    except Exception:
        return str(k)

world = None
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
except Exception as e:
    unreal.log(f"{TAG} world probe hata: {e}")

if not world:
    log("PIE", False, "PIE dunyasi yok - ONCE Play'e bas, sonra bu scripti kos")
else:
    log("PIE", True, world.get_name())
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    log("PC", pc is not None, pc.get_name() if pc else "yok")
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    log("PAWN", pawn is not None, f"{pawn.get_name()} ({pawn.get_class().get_name()})" if pawn else "possess yok")

    subsys = None
    if pc:
        try:
            subsys = unreal.SubsystemBlueprintLibrary.get_local_player_sub_system_from_player_controller(
                pc, unreal.EnhancedInputLocalPlayerSubsystem)
        except Exception as e:
            log("SUBSYS", False, e)
    log("SUBSYS", subsys is not None, "EnhancedInputLocalPlayerSubsystem")

    imc = unreal.EditorAssetLibrary.load_asset("/Game/vehicle/IMC_AF_Drive")
    ias = {n: unreal.EditorAssetLibrary.load_asset(f"/Game/vehicle/{n}")
           for n in ("IA_Throttle", "IA_Brake", "IA_Steer")}
    log("ASSETS", bool(imc) and all(ias.values()), "IMC + 3 IA yuklendi")

    if subsys and imc:
        # 1) Kayitli mi? (INI + BP BeginPlay yollarinin toplam sonucu)
        try:
            has = subsys.has_mapping_context(imc)
        except Exception as e:
            has = None
            log("HAS_IMC", False, f"API hata: {e}")
        if has is not None:
            log("HAS_IMC_ONCE", bool(has), f"add oncesi kayitli mi: {has}")

        # 2) Aksiyonlara mapli tuslar (add oncesi)
        for n, ia in ias.items():
            if not ia: continue
            try:
                keys = subsys.query_keys_mapped_to_action(ia)
                log(f"KEYS_{n}_ONCE", len(keys) > 0, [keyname(k) for k in keys])
            except Exception as e:
                log(f"KEYS_{n}_ONCE", False, f"API hata: {e}")

        # 3) Eksikse runtime'a ekle
        added = False
        try:
            if not has:
                subsys.add_mapping_context(imc, 0)
                added = True
        except Exception as e:
            log("ADD_IMC", False, e)
        if added:
            log("ADD_IMC", True, "IMC_AF_Drive runtime'a eklendi (priority 0)")

        # 4) Add sonrasi tekrar olc
        try:
            log("HAS_IMC_SONRA", bool(subsys.has_mapping_context(imc)), "")
        except Exception as e:
            log("HAS_IMC_SONRA", False, e)
        for n, ia in ias.items():
            if not ia: continue
            try:
                keys = subsys.query_keys_mapped_to_action(ia)
                log(f"KEYS_{n}_SONRA", len(keys) > 0, [keyname(k) for k in keys])
            except Exception as e:
                log(f"KEYS_{n}_SONRA", False, f"API hata: {e}")

unreal.log(f"{TAG} ===== OTOMATIK KONTROL =====")
for n, s, i in R:
    unreal.log(f"{TAG} {n:18s}: {s}  ({i})")
fails = [n for n, s, _ in R if s == "FAIL"]

if fails:
    unreal.log(TAG + " SONUC FAIL: " + ",".join(fails))
else:
    unreal.log(TAG + " SONUC PASS - SIMDI viewport ICINE tikla, W bas; arac kipirdarsa haber ver")
