#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Y3 — Yayın web sayfaları yer tutucu doldurma kapısı.

docs/web/ altındaki sayfalar gerçek kişisel bilgi İÇERMEZ; iletişim/yayıncı
bilgileri {{...}} yer tutucularıdır. Bu betik docs/web'i hedef dizine KOPYALAR
(kaynağa dokunmaz) ve yer tutucuları verilen değerlerle doldurur.

Kullanım:
    python tools/web_doldur.py --yayinci "..." --adres "..." --eposta "..." \
        --ulke "..." --cikti <dizin>

Kapı (K11):
    - Dört değerden ve --cikti'den herhangi biri eksikse argparse KIRMIZI çıkarır.
    - Doldurma sonrası çıktıda tek bir `{{` kalırsa betik KIRMIZI çıkarır (exit 1)
      ve hangi dosyada kaldığını yazar.
    - E-posta en az bir '@' içermeli; içermiyorsa KIRMIZI.

Yer tutucular (docs/web): {{YAYINCI_ADI}} {{ADRES}} {{DESTEK_EPOSTA}} {{SUNUCU_ULKE}}
"""
import argparse
import html
import re
import shutil
import sys
from pathlib import Path

# Betik tools/ altında; kaynak docs/web repo köküne göredir.
KAYNAK = Path(__file__).resolve().parent.parent / "docs" / "web"

YER_TUTUCULAR = {
    "YAYINCI_ADI": None,
    "ADRES": None,
    "DESTEK_EPOSTA": None,
    "SUNUCU_ULKE": None,
}
TUTUCU_DESEN = re.compile(r"\{\{([A-Z_]+)\}\}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="docs/web yayın sayfalarını yer tutuculardan doldurup kopyalar."
    )
    ap.add_argument("--yayinci", required=True, help="Yayıncı adı (ör. şirket/kişi adı)")
    ap.add_argument("--adres", required=True, help="Yayıncı posta adresi")
    ap.add_argument("--eposta", required=True, help="Destek e-posta adresi")
    ap.add_argument("--ulke", required=True, help="Oyun sunucularının bulunduğu ülke")
    ap.add_argument("--cikti", required=True, help="Doldurulmuş sayfaların yazılacağı dizin")
    args = ap.parse_args()

    if "@" not in args.eposta:
        print("HATA: --eposta bir e-posta adresi gibi görünmüyor ('@' yok): %r" % args.eposta)
        return 1
    if not args.yayinci.strip() or not args.adres.strip() or not args.ulke.strip():
        print("HATA: --yayinci / --adres / --ulke boş olamaz.")
        return 1

    if not KAYNAK.is_dir():
        print("HATA: kaynak dizin yok: %s" % KAYNAK)
        return 1

    degerler = {
        "YAYINCI_ADI": html.escape(args.yayinci.strip()),
        "ADRES": html.escape(args.adres.strip()),
        "DESTEK_EPOSTA": html.escape(args.eposta.strip()),
        "SUNUCU_ULKE": html.escape(args.ulke.strip()),
    }

    cikti = Path(args.cikti)
    if cikti.exists():
        print("HATA: çıktı dizini zaten var, üzerine yazılmaz: %s" % cikti)
        return 1
    cikti.mkdir(parents=True)

    # Yalnız HTML dosyaları kopyalanır (docs/web'in tamamı yayına gider).
    dosyalar = sorted(KAYNAK.glob("*.html"))
    if not dosyalar:
        print("HATA: %s altında .html dosyası yok." % KAYNAK)
        return 1

    kalan_tutucu = []
    for dosya in dosyalar:
        metin = dosya.read_text(encoding="utf-8")
        bilinmeyen = [m for m in TUTUCU_DESEN.findall(metin) if m not in degerler]
        if bilinmeyen:
            print("HATA: %s içinde bilinmeyen yer tutucu(lar): %s" % (dosya.name, bilinmeyen))
            return 1
        for ad, deger in degerler.items():
            metin = metin.replace("{{%s}}" % ad, deger)
        if "{{" in metin:
            kalan_tutucu.append(dosya.name)
        (cikti / dosya.name).write_text(metin, encoding="utf-8", newline="\n")

    if kalan_tutucu:
        print("HATA: doldurulmamış yer tutucu kaldı: %s" % ", ".join(kalan_tutucu))
        return 1

    print("OK: %d dosya doldurulup %s altına yazıldı; '{{' kalmadı." % (len(dosyalar), cikti))
    return 0


if __name__ == "__main__":
    sys.exit(main())
