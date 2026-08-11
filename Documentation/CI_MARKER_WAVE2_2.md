# CI Marker - Wave 2, Batch 2

Amac: bu isaret dosyasi yalnizca bir pull request acabilmek ve boylece
`main` uzerine dogrudan gonderilmis commit'lerin CI ciktisini gorebilmek
icin vardir. Asla `main` icine birlestirilmez.

## Bu partinin kapsadigi commit'ler

| Dosya | Commit (kisa) | Boyut |
|---|---|---|
| Tools/af_track_drift_guard.py | d2afee20 | 30180 B |
| Tools/af_drift_guard.py | baa6427b | 38569 B |

## Ne dogrulanir

1. Her iki surukleme (drift) muhafizi da sozdizimsel olarak gecerli
   kalmistir. `Python syntax check` isi tum `.py` dosyalarini derler;
   eksik yazilmis (truncated) bir dosya burada kirmizi doner.
2. `af_static_validate` py3.9 ve py3.12 isleri hala gecer, yani urun adi
   degisikligi hicbir yapisal iddiayi bozmamistir.
3. Blender headless duman testi etkilenmemistir.

## Ne dogrulanmaz

- Hicbir C++ dosyasi derlenmemistir.
- Hicbir Unreal projesi acilmamistir.
- Hicbir mesh gorsel olarak incelenmemistir.
- Hicbir tur surulmemistir.

Yesil CI bu maddelerin hicbirini kanitlamaz.

## Kasitli olarak degistirilmeyenler

Her iki muhafizdaki modul dizini sabitleri (`PATH_TRACK_CPP`,
`PATH_TYPES_H`, `PATH_SECTOR_CPP`, `PATH_VALIDATOR_CPP`) hala eski
modul adlarini tasir. Bunlar gercek dosya sistemi yollaridir; modul
dizinleri yeniden adlandirilana kadar degistirilirse muhafiz kaynagini
bulamaz ve CI kirmizi doner. Bu, dalga 2A'da ayni commit icinde
yapilacaktir.
