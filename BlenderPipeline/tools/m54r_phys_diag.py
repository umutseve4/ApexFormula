import unreal
def gp(o, n):
    try:
        return o.get_editor_property(n)
    except Exception:
        return 'OKUNAMADI:' + n
w = unreal.EditorLevelLibrary.get_game_world()
pawns = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
pawn = None
comp = None
for a in pawns:
    pawn = a
    comp = a.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    break
unreal.log('=M54R= ===== OTOMATIK KONTROL =====')
if not comp:
    unreal.log('=M54R= PAWN YOK - Play acik mi?')
else:
    unreal.log('=M54R= mech_sim_enabled = %s' % gp(comp, 'mechanical_sim_enabled'))
    mesh = pawn.get_component_by_class(unreal.SkeletalMeshComponent)
    if mesh:
        unreal.log('=M54R= simulate_physics=%s kutle=%.1f kg' % (mesh.is_simulating_physics(), mesh.get_mass()))
    else:
        unreal.log('=M54R= MESH YOK')
    ds = gp(comp, 'differential_setup')
    if not isinstance(ds, str):
        unreal.log('=M54R= diff_type=%s split=%s' % (gp(ds, 'differential_type'), gp(ds, 'front_rear_split')))
    ts = gp(comp, 'transmission_setup')
    if not isinstance(ts, str):
        unreal.log('=M54R= otomatik=%s clutch=%s final=%s' % (gp(ts, 'use_automatic_gears'), gp(ts, 'transmission_efficiency'), gp(ts, 'final_ratio')))
    ws = gp(comp, 'wheel_setups')
    if not isinstance(ws, str):
        i = 0
        for s in ws:
            cls = gp(s, 'wheel_class')
            bone = gp(s, 'bone_name')
            if cls:
                cdo = unreal.get_default_object(cls)
                unreal.log('=M54R= teker%d bone=%s eng=%s axle=%s r=%s brk=%s' % (i, bone, gp(cdo, 'affected_by_engine'), gp(cdo, 'axle_type'), gp(cdo, 'wheel_radius'), gp(cdo, 'max_brake_torque')))
            else:
                unreal.log('=M54R= teker%d bone=%s CLASS YOK' % (i, bone))
            i = i + 1
