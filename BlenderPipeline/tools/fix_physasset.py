import unreal

ASSET = '/Game/Vehicle/AF_Vehicle_Proto_PhysicsAsset'
OBJROOT = ASSET + '.AF_Vehicle_Proto_PhysicsAsset'
RADII = {'AF_Wheel_FL': 36.0, 'AF_Wheel_FR': 36.0, 'AF_Wheel_RL': 38.0, 'AF_Wheel_RR': 38.0}
print('===== OTOMATIK KONTROL =====')
pa = unreal.EditorAssetLibrary.load_asset(ASSET)
bodies = {}
for i in range(0, 20):
    try:
        o = unreal.load_object(None, OBJROOT + ':SkeletalBodySetup_' + str(i))
    except Exception:
        o = None
    if o:
        bn = str(o.get_editor_property('bone_name'))
        bodies[bn] = o
        print('body: ' + bn)
ok = 0
for bn, r in RADII.items():
    o = bodies.get(bn)
    if not o:
        print(bn + ' : BODY YOK (Add Bodies yapilmamis olabilir)')
        continue
    try:
        sp = unreal.KSphereElem()
        sp.set_editor_property('radius', r)
        ag = unreal.KAggregateGeom()
        ag.set_editor_property('sphere_elems', [sp])
        o.set_editor_property('agg_geom', ag)
        ok = ok + 1
        print(bn + ' : Sphere r=' + str(r) + ' yazildi')
    except Exception as e:
        print(bn + ' : FAIL ' + str(e))
ch = bodies.get('AF_Chassis')
chok = False
if ch:
    ag = ch.get_editor_property('agg_geom')
    nb = len(ag.get_editor_property('box_elems'))
    chok = nb == 1
    print('AF_Chassis : box=' + str(nb))
unreal.EditorAssetLibrary.save_loaded_asset(pa)
if ok == 4 and chok:
    print('SONUC : PASS - chassis Box + 4 tekerlek Sphere kaydedildi')
else:
    print('SONUC : FAIL - tekerlek ok=' + str(ok) + ' chassisBox=' + str(chok))
