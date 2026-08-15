# m54d_make_input_v2.py - D-092 M5.4d v2 (ASCII only)
# v1 FAIL: InputActionFactory / InputMappingContextFactory not exposed in UE 5.8.1 Python.
# v2 approach: InputAction and InputMappingContext both derive from UDataAsset,
# so create them with unreal.DataAssetFactory + data_asset_class (proven generic path).
import unreal

RESULTS = []
def log(tag, ok, msg):
    RESULTS.append((tag, ok))
    unreal.log("%s : %s - %s" % (tag, "PASS" if ok else "FAIL", msg))

unreal.log("===== OTOMATIK KONTROL =====")

AT = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
PKG = "/Game/vehicle"

def make_data_asset(name, klass):
    path = "%s/%s" % (PKG, name)
    if EAL.does_asset_exist(path):
        a = EAL.load_asset(path)
        if a:
            return a, "var olan yuklendi"
    f = unreal.DataAssetFactory()
    f.set_editor_property("data_asset_class", klass)
    a = AT.create_asset(name, PKG, klass, f)
    return a, "yeni olusturuldu"

# --- 1) Input Actions (Axis1D) ---
IAS = {}
for name in ("IA_Throttle", "IA_Brake", "IA_Steer"):
    tag = name.replace("IA_", "IA-").upper()
    try:
        ia, how = make_data_asset(name, unreal.InputAction)
        if ia is None:
            raise Exception("create_asset None dondu")
        ia.set_editor_property("value_type", unreal.InputActionValueType.AXIS1D)
        rb = ia.get_editor_property("value_type")
        ok = (rb == unreal.InputActionValueType.AXIS1D)
        IAS[name] = ia
        log(tag, ok, "%s value_type=%s" % (how, rb))
    except Exception as e:
        log(tag, False, repr(e))

# --- 2) Input Mapping Context ---
imc = None
try:
    imc, how = make_data_asset("IMC_AF_Drive", unreal.InputMappingContext)
    if imc is None:
        raise Exception("create_asset None dondu")
    log("IMC", True, how)
except Exception as e:
    log("IMC", False, repr(e))

# --- 3) Mappings: W/S/D plain, A with Negate ---
def make_key(name):
    try:
        return unreal.Key(name)
    except Exception:
        k = unreal.Key()
        k.set_editor_property("key_name", name)
        return k

if imc is not None and len(IAS) == 3:
    try:
        maps = imc.get_editor_property("mappings")
        new_maps = unreal.Array(unreal.EnhancedActionKeyMapping)
        plan = [("IA_Throttle", "W", False), ("IA_Brake", "S", False),
                ("IA_Steer", "D", False), ("IA_Steer", "A", True)]
        for ia_name, key, neg in plan:
            m = unreal.EnhancedActionKeyMapping()
            m.set_editor_property("action", IAS[ia_name])
            m.set_editor_property("key", make_key(key))
            if neg:
                mod = unreal.new_object(unreal.InputModifierNegate, outer=imc)
                mods = m.get_editor_property("modifiers")
                mods.append(mod)
                m.set_editor_property("modifiers", mods)
            new_maps.append(m)
        imc.set_editor_property("mappings", new_maps)
        rb = imc.get_editor_property("mappings")
        keys = ",".join(str(x.get_editor_property("key").get_editor_property("key_name")) for x in rb)
        ok = (len(rb) == 4)
        log("MAP", ok, "n=%d keys=%s" % (len(rb), keys))
    except Exception as e:
        log("MAP", False, repr(e))
else:
    log("MAP", False, "onkosul eksik (IMC veya IA'lar yok)")

# --- 4) Save ---
try:
    saved = []
    for name in ("IA_Throttle", "IA_Brake", "IA_Steer", "IMC_AF_Drive"):
        p = "%s/%s" % (PKG, name)
        if EAL.does_asset_exist(p):
            saved.append(EAL.save_asset(p, only_if_is_dirty=False))
        else:
            saved.append(False)
    ok = all(saved)
    log("SAVE", ok, "kaydedilen=%s" % saved)
except Exception as e:
    log("SAVE", False, repr(e))

fails = [t for t, ok in RESULTS if not ok]
if not fails:
    unreal.log("SONUC : PASS - M5.4d asset katmani tamam; BP editor screenshot gonder (graph binding hibrit GUI)")
else:
    unreal.log("SONUC : FAIL - dusen adimlar: %s; TAM ciktiyi yapistir (2. FAIL = yontem degisir, D-087)" % ",".join(fails))
