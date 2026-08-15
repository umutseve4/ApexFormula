# m54d_make_input.py - D-092 M5.4d: Enhanced Input assets
# IA_Throttle / IA_Brake / IA_Steer (Axis1D) + IMC_AF_Drive (W/S/A/D)
# ASCII only. OTOMATIK KONTROL cikti standardi.
import unreal

results = []
def log(tag, ok, msg):
    results.append((tag, ok))
    unreal.log("%s : %s - %s" % (tag, "PASS" if ok else "FAIL", msg))

unreal.log("===== OTOMATIK KONTROL =====")

at = unreal.AssetToolsHelpers.get_asset_tools()
ar = unreal.AssetRegistryHelpers.get_asset_registry()
PKG = "/Game/vehicle"

# ---------- 1) InputAction x3 ----------
ia_assets = {}
try:
    ia_factory_cls = unreal.InputActionFactory
except AttributeError:
    ia_factory_cls = None

for name in ("IA_Throttle", "IA_Brake", "IA_Steer"):
    path = PKG + "/" + name
    try:
        a = unreal.EditorAssetLibrary.load_asset(path)
        if a is None:
            if ia_factory_cls is None:
                raise Exception("InputActionFactory yok (plugin Python yuzeyi kapali)")
            a = at.create_asset(name, PKG, unreal.InputAction, ia_factory_cls())
        if a is None:
            raise Exception("create_asset None dondu")
        try:
            a.set_editor_property("value_type", unreal.InputActionValueType.AXIS1D)
        except Exception as e:
            unreal.log("  UYARI %s value_type: %r" % (name, e))
        vt = a.get_editor_property("value_type")
        ia_assets[name] = a
        log("IA-" + name.split("_")[1].upper(), True, "path=%s value_type=%s" % (path, vt))
    except Exception as e:
        log("IA-" + name.split("_")[1].upper(), False, repr(e))

# ---------- 2) IMC ----------
imc = None
try:
    imc_path = PKG + "/IMC_AF_Drive"
    imc = unreal.EditorAssetLibrary.load_asset(imc_path)
    if imc is None:
        imc = at.create_asset("IMC_AF_Drive", PKG, unreal.InputMappingContext,
                              unreal.InputMappingContextFactory())
    if imc is None:
        raise Exception("IMC create_asset None dondu")
    log("IMC", True, "path=%s" % imc_path)
except Exception as e:
    log("IMC", False, repr(e))

# ---------- yardimcilar ----------
def make_key(key_name):
    try:
        return unreal.Key(key_name)
    except Exception:
        pass
    k = unreal.Key()
    k.set_editor_property("key_name", key_name)
    return k

def make_negate(outer):
    return unreal.new_object(unreal.InputModifierNegate, outer=outer)

# ---------- 3) Mappingler (copy -> modify -> set-back) ----------
if imc is not None and len(ia_assets) == 3:
    try:
        plan = [
            ("IA_Throttle", "W", False),
            ("IA_Brake",    "S", False),
            ("IA_Steer",    "D", False),
            ("IA_Steer",    "A", True),
        ]
        new_maps = []
        for ia_name, key_name, negate in plan:
            m = unreal.EnhancedActionKeyMapping()
            m.set_editor_property("action", ia_assets[ia_name])
            m.set_editor_property("key", make_key(key_name))
            if negate:
                m.set_editor_property("modifiers", [make_negate(imc)])
            new_maps.append(m)
        imc.set_editor_property("mappings", new_maps)
        rb = imc.get_editor_property("mappings")
        desc = []
        for m in rb:
            act = m.get_editor_property("action")
            key = m.get_editor_property("key")
            nmods = len(m.get_editor_property("modifiers"))
            desc.append("%s<-%s(mod=%d)" % (act.get_name() if act else "None",
                                            str(key.get_editor_property("key_name")), nmods))
        ok = (len(rb) == 4)
        log("MAP", ok, " | ".join(desc))
    except Exception as e:
        log("MAP", False, repr(e))
else:
    log("MAP", False, "onkosul eksik (IMC veya IA'lar yok)")

# ---------- 4) SAVE ----------
try:
    ok = True
    for p in ("/Game/vehicle/IA_Throttle", "/Game/vehicle/IA_Brake",
              "/Game/vehicle/IA_Steer", "/Game/vehicle/IMC_AF_Drive"):
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            ok = unreal.EditorAssetLibrary.save_asset(p) and ok
        else:
            ok = False
    log("SAVE", ok, "4 asset kaydedildi" if ok else "en az bir asset kaydedilemedi")
except Exception as e:
    log("SAVE", False, repr(e))

failed = [t for t, o in results if not o]
if failed:
    unreal.log("SONUC : FAIL - dusen adimlar: %s; TAM ciktiyi yapistir" % ",".join(failed))
else:
    unreal.log("SONUC : PASS - M5.4d asset katmani tamam; pawn input baglama (graph) icin BP editor screenshot gonder")
