import unreal

S = dict(n=0, t=0.0, gmin=99, gmax=-99, tgmin=99, tgmax=-99,
         rpm=0.0, fwd=0.0, done=False, h=None, mm=None)

def find_mm():
    w = unreal.EditorLevelLibrary.get_game_world()
    if w is None:
        return None
    pawns = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
    first = None
    for a in pawns:
        first = a
        break
    if first is None:
        return None
    return first.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)

def tick(dt):
    if S.get("done"):
        return
    S.update(t=S.get("t") + dt)
    if S.get("mm") is None:
        S.update(mm=find_mm())
        if S.get("mm") is None:
            return
    mm = S.get("mm")
    try:
        g  = mm.get_current_gear()
        tg = mm.get_target_gear()
        r  = mm.get_engine_rotation_speed()
        f  = abs(mm.get_forward_speed())
    except Exception as e:
        unreal.log("[M54P] SAMPLE FAIL " + str(e))
        S.update(done=True)
        unreal.unregister_slate_post_tick_callback(S.get("h"))
        return
    S.update(n=S.get("n") + 1,
             gmin=min(S.get("gmin"), g), gmax=max(S.get("gmax"), g),
             tgmin=min(S.get("tgmin"), tg), tgmax=max(S.get("tgmax"), tg),
             rpm=max(S.get("rpm"), r), fwd=max(S.get("fwd"), f))
    if S.get("t") >= 10.0:
        S.update(done=True)
        unreal.unregister_slate_post_tick_callback(S.get("h"))
        unreal.log("[M54P] ===== OTOMATIK KONTROL =====")
        unreal.log("[M54P] ornek sayisi : %d" % S.get("n"))
        unreal.log("[M54P] gear  min/max: %d / %d" % (S.get("gmin"), S.get("gmax")))
        unreal.log("[M54P] tgear min/max: %d / %d" % (S.get("tgmin"), S.get("tgmax")))
        unreal.log("[M54P] rpm max      : %.0f" % S.get("rpm"))
        unreal.log("[M54P] fwd max cm/s : %.1f" % S.get("fwd"))
        if S.get("gmax") == 0:
            unreal.log("[M54P] TESHIS: VITES BOSTA (gear hep 0) = sanziman devreye girmiyor")
        else:
            unreal.log("[M54P] TESHIS: vites giriyor, sorun baska katmanda")

S.update(h=unreal.register_slate_post_tick_callback(tick))
unreal.log("[M54P] basladi - 10 sn boyunca W'ye bas!")
