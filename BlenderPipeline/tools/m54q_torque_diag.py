import unreal, time
curve = unreal.load_asset('/Game/vehicle/Curve_AF_Torque.Curve_AF_Torque')
unreal.log('=M54Q= ===== CURVE KONTROL =====')
if curve:
    for x in (0.0, 1200.0, 3000.0, 7000.0):
        unreal.log('=M54Q= curve(%.0f) = %.1f' % (x, curve.get_float_value(x)))
else:
    unreal.log('=M54Q= CURVE YUKLENEMEDI')
w = unreal.EditorLevelLibrary.get_game_world()
pawns = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
comp = None
for a in pawns:
    comp = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    break
if not comp:
    unreal.log('=M54Q= PAWN YOK - Play acik mi?')
else:
    try:
        es = comp.get_editor_property('engine_setup')
        mt = es.get_editor_property('max_torque')
        mr = es.get_editor_property('max_rpm')
        ir = es.get_editor_property('engine_idle_rpm')
        unreal.log('=M54Q= max_torque=%s max_rpm=%s idle_rpm=%s' % (mt, mr, ir))
    except Exception as e:
        unreal.log('=M54Q= engine_setup okunamadi: %s' % e)
    S = dict(t0=time.time(), rpm=0.0, fwd=0.0, h=None)
    def tick(dt):
        comp.set_throttle_input(1.0)
        try:
            comp.set_handbrake_input(False)
        except Exception:
            pass
        r = comp.get_engine_rotation_speed()
        f = abs(comp.get_forward_speed())
        if r > S.get('rpm'):
            S.update(rpm=r)
        if f > S.get('fwd'):
            S.update(fwd=f)
        if time.time() - S.get('t0') > 8.0:
            unreal.unregister_slate_post_tick_callback(S.get('h'))
            unreal.log('=M54Q= ===== OTOMATIK KONTROL =====')
            unreal.log('=M54Q= rpm max: %.0f' % S.get('rpm'))
            unreal.log('=M54Q= fwd max: %.1f cm/s' % S.get('fwd'))
            if S.get('rpm') > 1500.0:
                unreal.log('=M54Q= SONUC: TORK GELDI - gaz yolu calisiyor')
            else:
                unreal.log('=M54Q= SONUC: RPM HALA KILITLI - fizik katmani')
    h = unreal.register_slate_post_tick_callback(tick)
    S.update(h=h)
    unreal.log('=M54Q= basladi - 8 sn script kendisi gaza basiyor, tusa DOKUNMA')
