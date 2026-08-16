import unreal
eal = unreal.EditorAssetLibrary
paths = eal.list_assets('/Game/vehicle', recursive=True, include_folder=False)
fixed = 0
for pth in paths:
    a = eal.load_asset(pth)
    if isinstance(a, unreal.Blueprint):
        gc = a.generated_class()
        if gc:
            cdo = unreal.get_default_object(gc)
            if isinstance(cdo, unreal.ChaosVehicleWheel):
                nm = a.get_name().lower()
                on = ('_fl' in nm) or ('_fr' in nm) or ('front' in nm) or ('_f' == nm.replace('bp_af_wheel',''))
                if on:
                    ax = unreal.AxleType.FRONT
                else:
                    ax = unreal.AxleType.REAR
                cdo.set_editor_property('axle_type', ax)
                ok = eal.save_loaded_asset(a)
                geri = cdo.get_editor_property('axle_type')
                unreal.log('=M54S= %s -> %s save=%s geri_okuma=%s' % (a.get_name(), ax, ok, geri))
                fixed = fixed + 1
unreal.log('=M54S= ===== OTOMATIK KONTROL =====')
if fixed > 0:
    unreal.log('=M54S= PASS - %d teker sinifi guncellendi' % fixed)
else:
    unreal.log('=M54S= FAIL - hic teker sinifi bulunamadi')
