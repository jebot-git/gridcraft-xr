# GridCraft for DomeD

This branch ports the pinned Storytold engine to the shared DomeD native base.
The upstream application and document engine remain authoritative. The native
frontend uses DomeD's FLTK/GPU window, bitmap UI fonts, universal menu and
current desktop/XR realm. The original upstream frontend is retained separately.

The shared frontend is fetched from `https://github.com/jebot-git/dome-craft-base.git` at the immutable revision
in `base.lock.json`; it is not copied into each application fork. The office
engines use that same base's BDF shaping/rendering provider. PhotoCraft retains
its upstream image/type compositor with bitmap native UI text.

```sh
python3 native/domed/build.py --domed-source ../DomeD \
  --toolkit /opt/fltk-vr/toolkit
native/domed/_build/gridcraft-domed --workspace /path/to/documents
```

Requirements: Rust, Python, CMake, C++20, canonical DomeD source, its patched FLTK
1.4.5 toolkit, installed Unicode BDF fonts, OpenGL/EGL, GIO, Wayland, X11 metadata,
Fontconfig, FreeType, zlib, nlohmann-json and Poppler's `pdftoppm` for office page
previews. A healthy desktop session bus supplies the universal-menu connection.
No new compositor, font assets, Qt/GTK frontend or ArtCraft AI app is included.

`--base-source` reuses an existing clean shared-base checkout at the locked SHA.
`--engine-dir` reuses separately built engines for frontend development. Build
outputs live under `native/domed/_build` and are excluded from source control.

See the shared base's [office implementation](https://github.com/jebot-git/dome-craft-base/blob/main/OFFICE-PORT.md)
and [PhotoCraft implementation](https://github.com/jebot-git/dome-craft-base/blob/main/PHOTO-PORT.md)
for validation and remaining development limits. Bitmap office PDFs currently
lack searchable text; bespoke-panel and physical XR parity are not certified.
