import unreal
w = unreal.EditorLevelLibrary.get_game_world()
pawns = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
p = None
for a in pawns:
    p = a
    break
mv = p.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
p.add_actor_world_offset(unreal.Vector(0.0, 0.0, 400.0), False, False)
S = dict(t=0.0, z0=p.get_actor_location().z, zmin=999999.0, rpmmax=0.0)
H = dict()
def tick(dt):
    S.update(t=S.get("t") + dt)
    mv.set_handbrake_input(False)
    mv.set_throttle_input(1.0)
    z = p.get_actor_location().z
    if z < S.get("zmin"):
        S.update(zmin=z)
    r = mv.get_engine_rotation_speed()
    if r > S.get("rpmmax"):
        S.update(rpmmax=r)
    if S.get("t") > 6.0:
        unreal.unregister_slate_post_tick_callback(H.get("h"))
        mv.set_throttle_input(0.0)
        dus = S.get("z0") - S.get("zmin")
        unreal.log("=M54U= ===== OTOMATIK KONTROL =====")
        unreal.log("=M54U= baslangic z: %.1f  dusme: %.1f cm" % (S.get("z0"), dus))
        unreal.log("=M54U= rpm max: %.0f" % S.get("rpmmax"))
        if S.get("rpmmax") > 2000.0:
            unreal.log("=M54U= SONUC: MOTOR SAGLAM - sorun zemin/carpisma katmani")
        else:
            unreal.log("=M54U= SONUC: MOTOR OLU - transmisyon/engine sim ici")
        if dus < 50.0:
            unreal.log("=M54U= UYARI: arac dusmuyor - fizik/gravity de subheli")
unreal.log("=M54U= arac 4m havaya kaldirildi, 6 sn gaz - DOKUNMA")
H.update(h=unreal.register_slate_post_tick_callback(tick))
