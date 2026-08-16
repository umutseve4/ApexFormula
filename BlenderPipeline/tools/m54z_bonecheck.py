import unreal
w = unreal.EditorLevelLibrary.get_game_world()
def log(s): unreal.log("=M54Z= " + str(s))
pawn = None
for p in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Pawn):
    if "BP_AF_VehiclePawn" in p.get_name(): pawn = p
if pawn is None:
    log("SONUC: FAIL - pawn bulunamadi (Play acik mi?)")
else:
    log("===== OTOMATIK KONTROL =====")
    ok = True
    mc = pawn.get_movement_component()
    log("pawn.get_movement_component = " + (mc.get_class().get_name() if mc else "None"))
    comps = pawn.get_components_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    vmc = comps[0] if len(comps) > 0 else None
    ayni = (mc is not None and vmc is not None and mc == vmc)
    log("chaos comp sayisi = " + str(len(comps)) + "   resmi movement comp ile AYNI mi: " + str(ayni))
    if not ayni: ok = False
    upd = None
    try: upd = vmc.get_editor_property("updated_component")
    except Exception as e: log("updated_component okunamadi: " + repr(e))
    log("updated_component = " + ((upd.get_name() + " (" + upd.get_class().get_name() + ")") if upd else "None"))
    if upd is None: ok = False
    meshes = pawn.get_components_by_class(unreal.SkeletalMeshComponent)
    mesh = meshes[0] if len(meshes) > 0 else None
    bones = []
    if mesh is None:
        log("SkeletalMeshComponent YOK"); ok = False
    else:
        n = mesh.get_num_bones()
        i = 0
        while i < n:
            bones.append(str(mesh.get_bone_name(i))); i += 1
        log("mesh = " + mesh.get_name() + "   bone sayisi = " + str(n))
        log("bones = " + ", ".join(bones))
        ma = None
        for prop in ("skeletal_mesh_asset", "skeletal_mesh"):
            try:
                ma = mesh.get_editor_property(prop)
                if ma: break
            except Exception: pass
        pa = None
        if ma:
            try: pa = ma.get_editor_property("physics_asset")
            except Exception as e: log("physics_asset okunamadi: " + repr(e))
        log("physics_asset = " + (pa.get_name() if pa else "None"))
        if pa is None: ok = False
        else:
            try:
                bodies = pa.get_editor_property("skeletal_body_setups")
                log("physics body sayisi = " + str(len(bodies)))
                for b in bodies:
                    log("  body bone: " + str(b.get_editor_property("bone_name")))
                if len(bodies) == 0: ok = False
            except Exception as e: log("body listesi okunamadi: " + repr(e))
    if vmc is not None:
        try:
            ws = vmc.get_editor_property("wheel_setups")
            idx = 0
            for s in ws:
                bn = str(s.get_editor_property("bone_name"))
                var = bn in bones
                if (bn == "") or (bn == "None") or (not var): ok = False
                log("wheel" + str(idx) + " bone='" + bn + "'   iskelette var mi: " + str(var))                
                idx += 1
        except Exception as e:
            ok = False; log("wheel_setups okunamadi: " + repr(e))
    else:
        ok = False
    if ok:
        log("SONUC: PASS - baglanti katmani SAGLAM; siradaki: minimal taze arac A/B testi")
    else:
        log("SONUC: FAIL - KOPUK KATMAN BULUNDU; ilk False/None satiri suclu, fix scripti sirada")
