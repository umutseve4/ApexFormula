# -*- coding: ascii -*-
# reimport_vehicle.py - D-089: AF_Vehicle_Proto.fbx'i script ile yeniden import eder
# ve sonucu OTOMATIK KONTROL blogu ile dogrular.
# Kosum (UE Output Log): py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/reimport_vehicle.py"
import unreal

FBX = 'C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/exports/AF_Vehicle_Proto.fbx'
DEST = '/Game/Vehicle'
MESH_PATH = '/Game/Vehicle/AF_Vehicle_Proto.AF_Vehicle_Proto'
PA_PKG = '/Game/Vehicle/AF_Vehicle_Proto_PhysicsAsset'

fails = []

# --- 1) Import task (var olan asset'in uzerine yazar) ---
opts = unreal.FbxImportUI()
opts.set_editor_property('import_mesh', True)
opts.set_editor_property('import_as_skeletal', True)
opts.set_editor_property('import_animations', False)
opts.set_editor_property('import_materials', False)
opts.set_editor_property('import_textures', False)
opts.set_editor_property('create_physics_asset', False)
sm = opts.skeletal_mesh_import_data
sm.set_editor_property('import_morph_targets', False)
sm.set_editor_property('use_t0_as_ref_pose', False)
sm.set_editor_property('convert_scene', True)
sm.set_editor_property('import_uniform_scale', 1.0)

task = unreal.AssetImportTask()
task.set_editor_property('filename', FBX)
task.set_editor_property('destination_path', DEST)
task.set_editor_property('replace_existing', True)
task.set_editor_property('automated', True)
task.set_editor_property('save', True)
task.set_editor_property('options', opts)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

print('===== OTOMATIK KONTROL =====')

# --- 2) Mesh yuklendi mi + bounds ---
mesh = unreal.load_object(None, MESH_PATH)
if mesh is None:
    fails.append('MESH')
    print('MESH   : FAIL - yuklenemedi')
else:
    b = mesh.get_imported_bounds()
    ext = b.box_extent
    dx, dy, dz = ext.x * 2, ext.y * 2, ext.z * 2
    ok = abs(dx - 560.0) <= 5.0
    print('BOUNDS : %s - X=%.2f Y=%.2f Z=%.2f cm (hedef X 560 +- 5)'
          % ('PASS' if ok else 'FAIL', dx, dy, dz))
    if not ok:
        fails.append('BOUNDS')

    # --- 3) Root kemik scale (1,1,1) ---
    skel = mesh.get_editor_property('skeleton')
    root_ok = True
    try:
        pose = unreal.SkeletalMeshEditorSubsystem  # varlik kontrolu icin degil; asagida ref pose okunur
    except Exception:
        pass
    try:
        ref = mesh.get_editor_property('ref_skeleton')
    except Exception:
        ref = None
    # ref_skeleton Python'a acik degilse aktor uzerinden okunur
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
    try:
        comp = actor.skeletal_mesh_component
        try:
            comp.set_skeletal_mesh_asset(mesh)
        except Exception:
            comp.set_editor_property('skeletal_mesh_asset', mesh)
        names = [str(n) for n in comp.get_all_socket_names()]
        root = 'AF_Root' if 'AF_Root' in names else (names[0] if names else None)
        if root:
            tr = comp.get_socket_transform(root, unreal.RelativeTransformSpace.RTS_COMPONENT)
            s = tr.scale3d
            root_ok = all(abs(v - 1.0) <= 0.001 for v in (s.x, s.y, s.z))
            print('ROOT   : %s - %s scale=(%.3f, %.3f, %.3f) (hedef 1,1,1)'
                  % ('PASS' if root_ok else 'FAIL', root, s.x, s.y, s.z))
        else:
            root_ok = False
            print('ROOT   : FAIL - kemik listesi bos')
    finally:
        eas.destroy_actor(actor)
    if not root_ok:
        fails.append('ROOT')

# --- 4) PhysAsset 5 body korunmus mu ---
n = 0
for i in range(0, 20):
    o = unreal.load_object(None, '%s.AF_Vehicle_Proto_PhysicsAsset:SkeletalBodySetup_%d' % (PA_PKG, i))
    if o is not None:
        n += 1
ok = (n == 5)
print('PHYSA  : %s - %d body bulundu (hedef 5)' % ('PASS' if ok else 'FAIL', n))
if not ok:
    fails.append('PHYSA')

if fails:
    print('SONUC : FAIL - %s dustu; ciktiyi yapistir' % ','.join(fails))
else:
    print('SONUC : PASS - reimport tamam, accept_m53.py kosumuna gec')
