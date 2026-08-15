# accept_m53.py - M5.3 sayisal kabul (paste-only, GUI yok)
# Kontroller:
#   A) Dingil mesafesi (FL-RL ve FR-RR, X ekseni)  : 360 +- 1 cm
#   B) Arac boyu (mesh bounds X)                    : 560 +- 5 cm
#   C) +X ileri: on tekerlek X > arka tekerlek X
#   D) Sasi kemigi Z = 28 +- 1 cm (chassis_top/2 = 0.28 m; D-089 duzeltmesi:
#      sasi kemigi TASARIM GEREGI tekerlek merkezlerinin (36/38 cm) altindadir,
#      eski "sasi Z > tekerlek Z" kontrolu tasarima aykiriydi)
import unreal

MESH_PATH = '/Game/Vehicle/AF_Vehicle_Proto.AF_Vehicle_Proto'
WHEELS = ['AF_Wheel_FL', 'AF_Wheel_FR', 'AF_Wheel_RL', 'AF_Wheel_RR']
CHASSIS = 'AF_Chassis'

results = []

def check(name, ok, detail):
    results.append((name, ok, detail))
    unreal.log('%s : %s - %s' % (name, 'PASS' if ok else 'FAIL', detail))

unreal.log('===== OTOMATIK KONTROL =====')

mesh = unreal.load_object(None, MESH_PATH)
if not mesh:
    unreal.log('SONUC : FAIL - mesh yuklenemedi: ' + MESH_PATH)
else:
    # --- B: mesh bounds ---
    try:
        bounds = mesh.get_imported_bounds()
        length = bounds.box_extent.x * 2.0
        check('B-BOY', abs(length - 560.0) <= 5.0, 'bounds X = %.2f cm (hedef 560 +- 5)' % length)
    except Exception as e:
        check('B-BOY', False, 'bounds okunamadi: %s' % e)

    # --- Kemik konumlari icin gecici aktor ---
    actor = None
    try:
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        actor = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
        comp = actor.skeletal_mesh_component
        set_ok = False
        for setter in ('set_skeletal_mesh_asset', 'set_skinned_asset_and_update', 'set_skeletal_mesh'):
            if hasattr(comp, setter):
                try:
                    getattr(comp, setter)(mesh)
                    set_ok = True
                    break
                except Exception:
                    pass
        if not set_ok:
            comp.set_editor_property('skeletal_mesh_asset', mesh)

        pos = {}
        for b in WHEELS + [CHASSIS]:
            p = comp.get_socket_location(b)
            pos[b] = p
            unreal.log('  kemik %s : X=%.2f Y=%.2f Z=%.2f' % (b, p.x, p.y, p.z))

        # --- A: dingil mesafesi ---
        wb_l = abs(pos['AF_Wheel_FL'].x - pos['AF_Wheel_RL'].x)
        wb_r = abs(pos['AF_Wheel_FR'].x - pos['AF_Wheel_RR'].x)
        check('A-DINGIL-SOL', abs(wb_l - 360.0) <= 1.0, 'FL-RL X farki = %.2f cm (hedef 360 +- 1)' % wb_l)
        check('A-DINGIL-SAG', abs(wb_r - 360.0) <= 1.0, 'FR-RR X farki = %.2f cm (hedef 360 +- 1)' % wb_r)

        # --- C: +X ileri ---
        fwd_ok = (pos['AF_Wheel_FL'].x > pos['AF_Wheel_RL'].x) and (pos['AF_Wheel_FR'].x > pos['AF_Wheel_RR'].x)
        check('C-ILERI+X', fwd_ok, 'on X (%.1f/%.1f) > arka X (%.1f/%.1f)' % (
            pos['AF_Wheel_FL'].x, pos['AF_Wheel_FR'].x, pos['AF_Wheel_RL'].x, pos['AF_Wheel_RR'].x))

        # --- D: sasi kemigi yuksekligi (D-089) ---
        # Hedef: chassis_origin_m() = chassis_top/2 = 0.28 m = 28 cm.
        # Tekerlek merkezleri 36/38 cm'dedir; sasi kemigi bunlarin ALTINDA olmak
        # zorundadir. Eski kontrol (sasi Z > tekerlek ort. Z) tasarim geregi
        # hicbir dogru veride gecemezdi.
        check('D-SASI-Z', abs(pos[CHASSIS].z - 28.0) <= 1.0,
              'sasi Z = %.2f cm (hedef 28 +- 1; D-089)' % pos[CHASSIS].z)

        # ekstra bilgi (kabul disi): iz genisligi
        track_f = abs(pos['AF_Wheel_FL'].y - pos['AF_Wheel_FR'].y)
        track_r = abs(pos['AF_Wheel_RL'].y - pos['AF_Wheel_RR'].y)
        unreal.log('  bilgi: iz genisligi on=%.2f arka=%.2f cm' % (track_f, track_r))
    except Exception as e:
        check('KEMIK-OLCUM', False, 'aktor/socket hatasi: %s' % e)
    finally:
        if actor:
            try:
                actor.destroy_actor()
            except Exception:
                pass

    n_fail = sum(1 for _, ok, _ in results if not ok)
    if n_fail == 0 and results:
        unreal.log('SONUC : PASS - M5.3 sayisal kabul TAMAM (%d/%d)' % (len(results), len(results)))
    else:
        unreal.log('SONUC : FAIL - %d kontrol dustu' % n_fail)
