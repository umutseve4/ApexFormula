# m54l_fix_input.py - M5.4f drivetrain deneme #5: Enhanced Input onarimi
# TESHIS (m54k pasif test): insan girdisi de araca ulasmiyor -> RPM 1200 kilitli.
# KOK NEDEN ADAYLARI:
#   (1) IMC_AF_Drive icinde tus eslemesi YOK (M5.4d'de DataAssetFactory bos yaratti)
#   (2) IMC hicbir yerde register edilmiyor (pawn BeginPlay'de AddMappingContext yok)
# COZUM: (1) IA value_type=Axis1D + IMC'ye W/S/A/D eslemeleri yaz + save
#        (2) DefaultInput.ini'ye EnhancedInputDeveloperSettings DefaultMappingContexts ekle
#           (BP graph'a dokunmadan, motor IMC'yi her local player'a otomatik ekler)
# Play GEREKMEZ. Script sonrasi UE YENIDEN BASLATILMALI (ini ancak aciliste okunur).
import unreal, os

TAG = "[M54L]"
def log(m): unreal.log(TAG + " " + m)

results = []
def check(name, ok, detail):
    results.append((name, bool(ok), detail))
    log("%s %s  %s" % (name, "PASS" if ok else "FAIL", detail))

# ---------- 1) asset'leri bul ----------
ar = unreal.AssetRegistryHelpers.get_asset_registry()
def find_asset(name):
    f = unreal.ARFilter(package_paths=["/Game"], recursive_paths=True)
    for ad in ar.get_assets(f):
        if str(ad.asset_name) == name:
            return str(ad.package_name)
    return None

paths = {}
for n in ["IMC_AF_Drive", "IA_Throttle", "IA_Brake", "IA_Steer"]:
    p = find_asset(n)
    paths[n] = p
    check("FIND_" + n, p is not None, str(p))

if not all(paths.values()):
    log("SONUC FAIL - asset(ler) bulunamadi, devam edilemiyor")
else:
    eal = unreal.EditorAssetLibrary
    imc = eal.load_asset(paths["IMC_AF_Drive"])
    ia_t = eal.load_asset(paths["IA_Throttle"])
    ia_b = eal.load_asset(paths["IA_Brake"])
    ia_s = eal.load_asset(paths["IA_Steer"])

    # ---------- 2) IA value_type = Axis1D (graph Action Value->float kullaniyor) ----------
    for name, ia in [("IA_Throttle", ia_t), ("IA_Brake", ia_b), ("IA_Steer", ia_s)]:
        try:
            before = str(ia.get_editor_property("value_type"))
            ia.set_editor_property("value_type", unreal.InputActionValueType.AXIS1D)
            after = str(ia.get_editor_property("value_type"))
            eal.save_loaded_asset(ia)
            check("VALTYPE_" + name, "AXIS1D" in after.upper(), "%s -> %s" % (before, after))
        except Exception as e:
            check("VALTYPE_" + name, False, repr(e))

    # ---------- 3) IMC mevcut eslemeleri raporla ----------
    try:
        old = imc.get_editor_property("mappings")
        log("IMC mevcut esleme sayisi=%d" % len(old))
        for m in old:
            log("  eski: action=%s key=%s" % (m.get_editor_property("action"),
                                              m.get_editor_property("key")))
    except Exception as e:
        log("IMC esleme okuma hatasi: " + repr(e))

    # ---------- 4) eslemeleri deterministik yeniden yaz ----------
    def key(kn):
        return unreal.Key(key_name=kn)

    def mapping(action, kn, negate=False):
        m = unreal.EnhancedActionKeyMapping()
        m.set_editor_property("action", action)
        m.set_editor_property("key", key(kn))
        if negate:
            neg = unreal.new_object(unreal.InputModifierNegate, outer=imc)
            m.set_editor_property("modifiers", [neg])
        return m

    try:
        new_maps = [
            mapping(ia_t, "W"),
            mapping(ia_b, "S"),
            mapping(ia_s, "D"),
            mapping(ia_s, "A", negate=True),
        ]
        imc.set_editor_property("mappings", new_maps)
        saved = eal.save_loaded_asset(imc)
        back = imc.get_editor_property("mappings")
        detail = "; ".join("%s->%s" % (m.get_editor_property("key"),
                                       m.get_editor_property("action").get_name())
                           for m in back)
        check("IMC_MAPPINGS", saved and len(back) == 4, "n=%d  %s" % (len(back), detail))
    except Exception as e:
        check("IMC_MAPPINGS", False, repr(e))

    # ---------- 5) DefaultInput.ini -> DefaultMappingContexts ----------
    try:
        ini = os.path.join(unreal.Paths.project_config_dir(), "DefaultInput.ini")
        obj_path = paths["IMC_AF_Drive"] + "." + paths["IMC_AF_Drive"].rsplit("/", 1)[-1]
        line = '+DefaultMappingContexts=(InputMappingContext="%s",Priority=0)' % obj_path
        section = "[/Script/EnhancedInput.EnhancedInputDeveloperSettings]"
        existing = ""
        if os.path.exists(ini):
            with open(ini, "r", encoding="utf-8", errors="replace") as f:
                existing = f.read()
        if "DefaultMappingContexts" in existing and obj_path in existing:
            check("INI", True, "zaten kayitli: " + line)
        else:
            with open(ini, "a", encoding="utf-8") as f:
                f.write("\n" + section + "\n" + line + "\n")
            with open(ini, "r", encoding="utf-8", errors="replace") as f:
                ok = obj_path in f.read()
            check("INI", ok, ini + "  <- " + line)
    except Exception as e:
        check("INI", False, repr(e))

    # ---------- OTOMATIK KONTROL ----------
    log("===== OTOMATIK KONTROL =====")
    allok = True
    for name, ok, detail in results:
        allok = allok and ok
        log("%-18s: %s  (%s)" % (name, "PASS" if ok else "FAIL", detail))
    log("SONUC %s" % ("PASS - UE'yi KAPAT/AC, sonra m54k kosumunu tekrarla" if allok
                      else "FAIL - ciktiyi raporla"))
