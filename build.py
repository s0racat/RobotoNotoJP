#!/usr/bin/python3

import subprocess
import os
from typing import Any, Tuple

import fontforge

VERSION = "v0.0.2"
FONT_NAME = "RobotoNotoJP"

BUILD_TMP = "build_tmp"
SOURCE_DIR = "source_fonts"
SOURCE_FONT_JP = "NotoSansJP-{}.ttf"
SOURCE_FONT_EN = "Roboto-{}.ttf"

EM_ASCENT = 1638
EM_DESCENT = 410

FONT_ASCENT = EM_ASCENT + 60
FONT_DESCENT = EM_DESCENT + 170

COPYRIGHT = """[Roboto]
Copyright (c) 2014 The Roboto Project Authors (https://github.com/googlefonts/roboto)

[NotoSansJP]
Copyright 2012 Google Inc.

[RobotoNotoJP]
Copyright 2023 soracat
"""

def open_font(weight: str) -> Tuple[Any, Any]:
    jp_font = fontforge.open(os.path.join(SOURCE_DIR, SOURCE_FONT_JP.format(weight)))
    en_font = fontforge.open(os.path.join(SOURCE_DIR, SOURCE_FONT_EN.format(weight)))
    return jp_font, en_font

def remove_duplicate_glyphs(jp_font, en_font):
    for g in en_font.glyphs():
        if not g.isWorthOutputting():
            continue
        unicode = int(g.unicode)
        if unicode >= 0:
            for g_jp in jp_font.selection.select(unicode).byGlyphs:
                g_jp.clear()


def merge_fonts(jp_font: Any, en_font: Any, weight: str) -> Any:
    em_size = EM_ASCENT + EM_DESCENT
    jp_font.em = em_size
    en_font.em = em_size

    en_font.generate(os.path.join(BUILD_TMP, f"modified_{SOURCE_FONT_JP.format(weight)}"))
    jp_font.mergeFonts(os.path.join(BUILD_TMP, f"modified_{SOURCE_FONT_JP.format(weight)}"))
    return jp_font


def edit_meta_data(font: Any, weight: str):
    font.ascent = EM_ASCENT
    font.descent = EM_DESCENT
    font.os2_typoascent = EM_ASCENT
    font.os2_typodescent = -EM_DESCENT

    font.hhea_ascent = FONT_ASCENT
    font.hhea_descent = -FONT_DESCENT
    font.os2_winascent = FONT_ASCENT
    font.os2_windescent = FONT_DESCENT
    font.hhea_linegap = 0
    font.os2_typolinegap = 0

    font.sfnt_names = (
        (
            "English (US)",
            "License",
            "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL",
        ),
        ("English (US)", "License URL", "http://scripts.sil.org/OFL"),
        ("English (US)", "Version", f"{FONT_NAME} {VERSION}"),
    )
    font.familyname = FONT_NAME
    font.fontname = f"{FONT_NAME}-{weight}"
    font.fullname = f"{FONT_NAME} {weight}"
    font.os2_vendor = "TWR"
    font.copyright = COPYRIGHT


def main():
    if not os.path.exists(BUILD_TMP):
        os.mkdir(BUILD_TMP)

    for weight in ("Regular", "Bold"):
        jp_font, en_font = open_font(weight)
        remove_duplicate_glyphs(jp_font,en_font)

        font = merge_fonts(en_font, jp_font, weight)

        edit_meta_data(font, weight)

        font.generate(os.path.join(BUILD_TMP, f"gen_{FONT_NAME}-{weight}.ttf"))

        subprocess.run(
            (
                "ttfautohint",
                "--dehint",
                os.path.join(BUILD_TMP, f"gen_{FONT_NAME}-{weight}.ttf"),
                os.path.join(BUILD_TMP, f"{FONT_NAME}-{weight}.ttf"),
            )
        )


if __name__ == "__main__":
    main()

