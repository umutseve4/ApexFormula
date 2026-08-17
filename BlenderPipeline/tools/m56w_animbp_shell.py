# m56w_animbp_shell.py - UludagFormula M5.6 (adim 1/2)
# DURUM: statik olarak yazildi, HIC CALISTIRILMADI (uzaktan UE editor yok).
# Amac: Wheel Controller AnimBP'sinin SHELL'ini Python'dan olusturmak.
# UE 5.8 Python AnimGraph node/pin YAZAMAZ (arastirma dogrulandi) ->
# Wheel Controller -> Output Pose baglantisi HER ZAMAN manuel editor isidir.
# Script sadece:
#   1) Arac skeletal mesh'inin Skeleton'unu bulur
#   2) parent=VehicleAnimationInstance, target_skeleton=o skeleton olan
#      ABP_Vehicle_Proto asset'ini olusturur; VARSA tip/skeleton/parent
#      dogrulamasi yapar, dogrulanamazsa FAIL verir (kor yeniden kullanmaz)
#   3) Arac Blueprint'inin SkeletalMeshComponent SINIF VARSAYILANINA (CDO)
#      animation_mode=ANIMATION_BLUEPRINT + anim_class icin ADAY atama dener.
#      Ayni oturumdaki geri-okuma cache'ten gelebilir; bu nedenle basari bile
#      "aday atama" olarak raporlanir ve KALICILIK EDITORDE DOGRULANMALIDIR
#      (asset'i kapat/ac veya editoru yeniden baslat, anim_class'i kontrol et).
#      Atama basarisiz olursa manuel editor atamasi gerekir.
# Kanit tabani: AnimBlueprintFactory.target_skeleton ve .parent_class RW;
# SkeletalMeshComponent.anim_class / .animation_mode RW (Epic Python API ref).
import unreal

PASS = True
LINES = []

def log(tag, ok, msg):
    global PASS
    s = "PASS" if ok else "FAIL"
    if not ok:
        PASS = False
    line = "[M56W] %s %s: %s" % (tag, s, msg)
    LINES.append(line)
    unreal.log(line)

def info(tag, msg):
    line = "[M56W] %s BILGI: %s" % (tag, msg)
    LINES.append(line)
    unreal.log(line)

def bail():
    print("\n".join(LINES))
    print("[M56W] SONUC: FAIL")
    raise SystemExit

ABP_DIR = "/Game/Vehicles"
ABP_NAME = "ABP_Vehicle_Proto"
ABP_PATH = "%s/%s" % (ABP_DIR, ABP_NAME)

ar = unreal.AssetRegistryHelpers.get_asset_registry()

# --- 1) Arac skeletal mesh + skeleton bul ---
sk_assets = [a for a in ar.get_assets_by_path("/Game", recursive=True)
             if str(a.asset_class_path.asset_name) == "SkeletalMesh"
             and "vehicle" in str(a.asset_name).lower()]
if not sk_assets:
    sk_assets = [a for a in ar.get_assets_by_path("/Game", recursive=True)
                 if str(a.asset_class_path.asset_name) == "SkeletalMesh"]
log("MESH_FIND", len(sk_assets) == 1,
    "skeletal mesh adaylari: %s" % [str(a.asset_name) for a in sk_assets])
if len(sk_assets) != 1:
    bail()

sk_mesh = sk_assets[0].get_asset()
skel = sk_mesh.get_editor_property("skeleton")
log("SKEL", skel is not None,
    "skeleton: %s" % (skel.get_name() if skel else "YOK"))
if skel is None:
    bail()

# --- 2) AnimBP shell olustur veya MEVCUDU DOGRULA ---
# NOT: Parent-class (ancestry) sorgusu icin dogrulanmis bir UE 5.8 Python
# API'si YOKTUR; bu nedenle ancestry hicbir zaman PASS kapisi olarak
# kullanilmaz. Yeni asset'te kanit factory parametresidir; mevcut asset'te
# ancestry EDITORDE dogrulanmalidir ve script atama yapmadan durur.
created = False
if unreal.EditorAssetLibrary.does_asset_exist(ABP_PATH):
    info("ABP", "%s zaten var - dogrulama yapiliyor (kor kullanim yok)" % ABP_PATH)
    abp = unreal.load_asset(ABP_PATH)
    is_abp = isinstance(abp, unreal.AnimBlueprint)
    log("ABP_TYPE", is_abp, "asset tipi AnimBlueprint mi: %s"
        % type(abp).__name__)
    if not is_abp:
        bail()
    try:
        abp_skel = abp.get_editor_property("target_skeleton")
    except Exception:
        abp_skel = None
    skel_ok = (abp_skel is not None
               and abp_skel.get_name() == skel.get_name())
    log("ABP_SKEL", skel_ok, "mevcut ABP target_skeleton: %s (beklenen %s)"
        % (abp_skel.get_name() if abp_skel else "YOK", skel.get_name()))
    if not skel_ok:
        bail()
else:
    factory = unreal.AnimBlueprintFactory()
    factory.set_editor_property("target_skeleton", skel)
    factory.set_editor_property("parent_class", unreal.VehicleAnimationInstance)
    abp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        ABP_NAME, ABP_DIR, unreal.AnimBlueprint, factory)
    log("ABP", abp is not None, "AnimBP shell olusturuldu: %s" % ABP_PATH)
    if abp is None:
        bail()
    created = True
    saved = unreal.EditorAssetLibrary.save_loaded_asset(abp)
    log("ABP_SAVE", saved, "AnimBP kaydedildi" if saved else "kayit basarisiz")
    if not saved:
        bail()  # kaydedilmemis shell'e referans veren BP save edilmemeli

# generated class + parent ancestry dogrulama (yeni VE mevcut icin)
gen_cls = None
try:
    gen_cls = unreal.EditorAssetLibrary.load_blueprint_class(ABP_PATH)
    info("ABP_CLASS", "generated class yuklendi: %s" % gen_cls.get_name())
except Exception as e:
    log("ABP_CLASS", False, "generated class yuklenemedi: %s" % e)
if gen_cls is None:
    bail()

if created:
    info("ABP_PARENT", "yeni asset: parent factory'de VehicleAnimationInstance "
         "olarak verildi (kanit=factory parametresi; nihai dogrulama yine de "
         "editorde Class Settings ekranindadir)")
else:
    # Mevcut asset: ancestry icin dogrulanmis Python API yok ->
    # ANCESTRY requires Unreal Editor verification; atama YAPILMAZ.
    log("ABP_PARENT", False,
        "mevcut asset parent'i Python'dan dogrulanamaz (dogrulanmis API yok) - "
        "ANCESTRY requires Unreal Editor verification: ABP'yi acip Class "
        "Settings > Parent Class alaninin VehicleAnimationInstance oldugunu "
        "dogrulayin; sonra anim_class atamasini manuel yapin")
    bail()

# --- 3) Arac BP SkeletalMeshComponent CDO'suna ADAY anim_class atamasi ---
bp_assets = [a for a in ar.get_assets_by_path("/Game", recursive=True)
             if str(a.asset_class_path.asset_name) == "Blueprint"
             and "vehicle" in str(a.asset_name).lower()]
info("BP_FIND", "arac BP adaylari: %s" % [str(a.asset_name) for a in bp_assets])
if len(bp_assets) == 1:
    bp_path = str(bp_assets[0].package_name)
    # Tum sinif/CDO/mesh/atama/kayit/geri-okuma adimlari KONTROLLU try
    # icindedir: hicbir hata yolu ETIKET+SONUC olmadan sonlanamaz.
    try:
        veh_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
        if veh_cls is None:
            raise RuntimeError("load_blueprint_class None dondu: %s" % bp_path)
        cdo = unreal.get_default_object(veh_cls)
        if cdo is None:
            raise RuntimeError("get_default_object None dondu")
        smc = cdo.get_editor_property("mesh")  # WheeledVehiclePawn.Mesh
        if smc is None:
            raise RuntimeError("SkeletalMeshComponent (cdo.mesh) None")
        smc.set_editor_property("animation_mode",
                                unreal.AnimationMode.ANIMATION_BLUEPRINT)
        smc.set_editor_property("anim_class", gen_cls)
        save_ok = unreal.EditorAssetLibrary.save_asset(bp_path)
        log("BP_SAVE", bool(save_ok),
            "arac BP save_asset sonucu: %s" % save_ok)
        # Ayni-oturum geri-okuma (cache'ten gelebilir - kanit DEGildir)
        re_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
        re_cdo = unreal.get_default_object(re_cls)
        re_smc = re_cdo.get_editor_property("mesh")
        re_ac = re_smc.get_editor_property("anim_class")
        re_am = re_smc.get_editor_property("animation_mode")
        reread_ok = (re_ac is not None
                     and re_ac.get_name() == gen_cls.get_name()
                     and re_am == unreal.AnimationMode.ANIMATION_BLUEPRINT)
        log("ASSIGN", bool(save_ok) and reread_ok,
            "ADAY atama: anim_class=%s animation_mode=%s (ayni-oturum "
            "geri-okuma; cache riski nedeniyle KALICILIK KANITI DEGIL)"
            % (re_ac.get_name() if re_ac else "None", re_am))
        info("ASSIGN_VERIFY", "KALICILIK DOGRULAMASI EDITOR ISIDIR: "
             "editoru yeniden baslatip arac BP'sinde Mesh > Anim Class "
             "alaninin ABP_Vehicle_Proto oldugunu kontrol edin. "
             "Persist etmediyse manuel atama gerekir.")
    except Exception as e:
        log("ASSIGN", False, "ADAY atama basarisiz: %s - manuel editor "
            "atamasi gerekir" % e)
else:
    log("ASSIGN", False,
        "atama yapilamadi (BP aday sayisi=%d, beklenen 1) - manuel editor "
        "atamasi gerekir" % len(bp_assets))

info("SONRAKI", "AnimGraph'ta Wheel Controller -> Output Pose baglantisi "
     "HER ZAMAN manuel editor isidir (Python yazamaz): ABP ac, AnimGraph'a "
     "WheelController node ekle, Output Pose'a bagla, Compile+Save.")
info("ETIKET", "Bu scriptin tum sonuclari 'requires Unreal Editor "
     "verification' etiketi tasir; PASS bile ayni-oturum aday sonucudur.")

print("\n".join(LINES))
print("[M56W] SONUC: %s" % ("PASS" if PASS else "FAIL"))
