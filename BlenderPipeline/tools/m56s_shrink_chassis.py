# m56s_shrink_chassis.py - UludagFormula M5.5
# Hipotez: oversized chassis collision box govdenin tekerleklerden once yere
# oturmasina yol aciyor -> suspansiyon raycast'leri zemine ulasmiyor -> torque var
# ama XY hareket yok. Fix: chassis box alt yuzeyini tekerlek merkezinin USTUNE cek.
# Arastirma kaniti: BodySetup.agg_geom Read-Write; struct copy->modify->reassign->save.
# bone_name Python'dan READ-ONLY (rebind dali gecersiz, m56r superseded).
import unreal

PASS = True
LINES = []

def log(tag, ok, msg):
    global PASS
    s = "PASS" if ok else "FAIL"
    if not ok:
        PASS = False
    line = "[M56S] %s %s: %s" % (tag, s, msg)
    LINES.append(line)
    unreal.log(line)

def info(tag, msg):
    line = "[M56S] %s BILGI: %s" % (tag, msg)
    LINES.append(line)
    unreal.log(line)

MARGIN_CM = 2.0

# --- 1) PhysicsAsset bul ---
ar = unreal.AssetRegistryHelpers.get_asset_registry()
pa_assets = [a for a in ar.get_assets_by_path("/Game", recursive=True)
             if str(a.asset_name) == "AF_Vehicle_Proto_PhysicsAsset"]
if not pa_assets:
    log("PA_FIND", False, "AF_Vehicle_Proto_PhysicsAsset bulunamadi")
    raise SystemExit
pa_path = str(pa_assets[0].package_name)
pa = unreal.load_asset(pa_path)
log("PA_FIND", pa is not None, pa_path)

# --- 2) Preview skeletal mesh + temp actor ---
# UE 5.8: preview_skeletal_mesh Python'a expose DEGIL (ARASTIRMACI dogruladi)
# -> try/except + iki kademeli fallback arama
prev_mesh = None
try:
    prev_mesh = pa.get_editor_property("preview_skeletal_mesh")
except Exception:
    info("MESH", "preview_skeletal_mesh UE 5.8 Python'da expose degil - fallback arama")
if prev_mesh is None:
    # fallback 1: ayni klasorde skeletal mesh ara
    folder = pa_path.rsplit("/", 1)[0]
    for a in ar.get_assets_by_path(folder, recursive=True):
        if str(a.asset_class_path.asset_name) == "SkeletalMesh":
            prev_mesh = a.get_asset()
            break
if prev_mesh is None:
    # fallback 2: /Game altinda adi AF_Vehicle iceren SkeletalMesh
    for a in ar.get_assets_by_path("/Game", recursive=True):
        if (str(a.asset_class_path.asset_name) == "SkeletalMesh"
                and "af_vehicle" in str(a.asset_name).lower()):
            prev_mesh = a.get_asset()
            break
log("MESH", prev_mesh is not None,
    "preview mesh: %s" % (prev_mesh.get_name() if prev_mesh else "YOK"))
if prev_mesh is None:
    raise SystemExit

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor = eas.spawn_actor_from_class(unreal.SkeletalMeshActor,
                                   unreal.Vector(0, 0, 10000))
smc = actor.skeletal_mesh_component
smc.set_skeletal_mesh_asset(prev_mesh)

# --- 3) Kemik listesi + tekerlek merkez z (actor space) ---
nbones = smc.get_num_bones()
bones = [str(smc.get_bone_name(i)) for i in range(nbones)]
info("BONES", ", ".join(bones))
wheel_bones = [b for b in bones if "wheel" in b.lower() or "whl" in b.lower()]
log("WHEELS", len(wheel_bones) >= 4, "tekerlek kemikleri: %s" % wheel_bones)

actor_z = actor.get_actor_location().z
wheel_zs = {}
for wb in wheel_bones:
    wt = smc.get_socket_transform(unreal.Name(wb),
                                  unreal.RelativeTransformSpace.RTS_ACTOR)
    wheel_zs[wb] = wt.translation.z
if wheel_zs:
    wheel_center_z = min(wheel_zs.values())
    info("WHEEL_Z", "actor-space tekerlek merkez z (min): %.1f  hepsi=%s"
         % (wheel_center_z, {k: round(v, 1) for k, v in wheel_zs.items()}))
else:
    log("WHEEL_Z", False, "tekerlek kemigi yok, hedef hesaplanamaz")
    eas.destroy_actor(actor)
    raise SystemExit

# --- 4..6) Body sec + box hesap + kaydet (QA: try/finally ile temizlik) ---
def run(actor, smc, eas):
    global PASS
    # 4) Body setup'lari ObjectIterator ile ENUMERATE et (isim tahmini YASAK - v2 FAIL nedeni)
    # v4 fix: unreal.SkeletalBodySetup 5.8'de expose degil (gap #14).
    # Plan A: parent sinif unreal.BodySetup ile iterate; Plan B: filtresiz iterate.
    # Her iki yolda da outer==pa + runtime class adi 'SkeletalBodySetup' filtresi.
    body_cls = getattr(unreal, "BodySetup", None)
    it = unreal.ObjectIterator(body_cls) if body_cls is not None else unreal.ObjectIterator()
    subs = [o for o in it
            if o.get_outer() == pa
            and o.get_class().get_name() == "SkeletalBodySetup"]
    info("ENUM", "%d SkeletalBodySetup bulundu (yol=%s)"
         % (len(subs), "BodySetup-iter" if body_cls is not None else "tam-iter"))
    candidates = []   # (idx, sub, bone, n_box, n_other)
    for i, sub in enumerate(subs):
        bn = str(sub.get_editor_property("bone_name"))
        agg0 = sub.get_editor_property("agg_geom")
        n_box = len(list(agg0.get_editor_property("box_elems")))
        n_oth = (len(list(agg0.get_editor_property("sphyl_elems")))
                 + len(list(agg0.get_editor_property("sphere_elems")))
                 + len(list(agg0.get_editor_property("convex_elems"))))
        info("BODY%d" % i, "bone=%s box=%d diger=%d" % (bn, n_box, n_oth))
        candidates.append((i, sub, bn, n_box, n_oth))

    # QA: sadece 'chassis/root/govde' iceren bone_name kabul; "ilk box'li" YASAK
    chassis = [c for c in candidates
               if any(k in c[2].lower() for k in ("chassis", "root", "govde", "body"))
               and c[3] > 0]
    if len(chassis) != 1:
        # tek body'li PA ise o body chassis'tir
        boxed = [c for c in candidates if c[3] > 0]
        if len(candidates) == 1 and len(boxed) == 1:
            chassis = boxed
        else:
            log("BODY", False,
                "chassis pozitif tanimlanamadi (aday=%d, boxlu=%d) - PhAT GUI gerekir"
                % (len(chassis), len(boxed)))
            return "FAIL"
    body_idx, found_body, bn = chassis[0][0], chassis[0][1], chassis[0][2]
    log("BODY", True, "body[%d] %s bone=%s secildi"
        % (body_idx, found_body.get_name(), bn))
    if chassis[0][4] > 0:
        log("BODY", False,
            "bu body'de box disi sekiller de var - script sadece box duzenler, PhAT GUI gerekir")
        return "FAIL"

    # 5) Bone->actor transform (scale dahil), box alt yuzey hesabi
    btf = smc.get_socket_transform(unreal.Name(bn),
                                   unreal.RelativeTransformSpace.RTS_ACTOR)
    scale_z = float(btf.scale3d.z)
    brot = btf.rotation.rotator()
    if abs(brot.pitch) + abs(brot.roll) > 1.0:
        log("BTF", False, "bone transform pitch/roll!=0 (%s) - dik hesap gecersiz, PhAT GUI"
            % brot)
        return "FAIL"
    info("BTF", "bone=%s scale.z=%.3f rot=%s" % (bn, scale_z, brot))

    agg = found_body.get_editor_property("agg_geom").copy()
    boxes = list(agg.get_editor_property("box_elems"))
    changed = False
    for i, b0 in enumerate(boxes):
        b = b0.copy()
        c = b.get_editor_property("center")
        rot = b.get_editor_property("rotation")
        if abs(rot.pitch) + abs(rot.roll) > 1.0:
            log("BOX%d" % i, False,
                "box rotation pitch/roll!=0 (%s) - degisiklik IPTAL, PhAT GUI" % rot)
            return "FAIL"
        ext_z_local = float(b.get_editor_property("z")) / 2.0
        ext_z_actor = ext_z_local * abs(scale_z)      # QA: scale ekstenti etkiler
        center_actor = btf.transform_location(c)
        bottom = center_actor.z - ext_z_actor
        top = center_actor.z + ext_z_actor
        info("BOX%d" % i, "actor-space bottom=%.1f top=%.1f (tekerlek merkez=%.1f)"
             % (bottom, top, wheel_center_z))
        target_bottom = wheel_center_z + MARGIN_CM
        if bottom >= target_bottom:
            info("BOX%d" % i, "zaten tekerlek ustunde - degisiklik yok")
            continue
        # QA aritmetigi: TOP SABIT kalir. Yeni actor-space merkez = (top+target)/2
        new_full_z_actor = top - target_bottom
        if new_full_z_actor < 10.0:
            log("BOX%d" % i, False,
                "yeni z boyu %.1fcm cok kucuk - manuel PhAT gerekir" % new_full_z_actor)
            return "FAIL"
        delta_center_actor = (target_bottom - bottom) / 2.0
        new_c = unreal.Vector(c.x, c.y, c.z + delta_center_actor / abs(scale_z))
        new_full_z_local = new_full_z_actor / abs(scale_z)
        b.set_editor_property("center", new_c)
        b.set_editor_property("z", new_full_z_local)
        boxes[i] = b
        changed = True
        info("BOX%d" % i, "FIX: bottom %.1f -> %.1f (top %.1f sabit; local z %.1f->%.1f)"
             % (bottom, target_bottom, top, ext_z_local * 2, new_full_z_local))

    if not changed:
        info("SONUC", "box zaten dogru - collision blocker degil; dogrudan m56m drive test")
        return "BILGI"

    # 6) Reassign + save + verify (transaction icinde)
    with unreal.ScopedEditorTransaction("m56s chassis box shrink"):
        agg.set_editor_property("box_elems", boxes)
        found_body.set_editor_property("agg_geom", agg)
    saved = unreal.EditorAssetLibrary.save_loaded_asset(pa)
    log("SAVE", saved, "PhysicsAsset kaydedildi" if saved else "kayit basarisiz")
    if not saved:
        return "FAIL"

    # verify: ayni nesneden agg_geom'u tekrar oku (isim tahminsiz)
    agg2 = found_body.get_editor_property("agg_geom")
    for j, bx in enumerate(list(agg2.get_editor_property("box_elems"))):
        info("VERIFY", "box%d persist: z=%.1f center=%s"
             % (j, float(bx.get_editor_property("z")),
                bx.get_editor_property("center")))
    return "PASS" if PASS else "FAIL"

try:
    sonuc = run(actor, smc, eas)
finally:
    eas.destroy_actor(actor)   # QA: her yolda temizlik

print("\n".join(LINES))
print("[M56S] SONUC: %s" % sonuc)
