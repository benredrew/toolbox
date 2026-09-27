# Toolbox

One pinned CAD and fabrication toolchain, with no design projects bundled.

Toolbox installs released versions of:

- [CadKit](https://github.com/benredrew/cadkit): model checks, drawings,
  engraving, and isolated viewers.
- [Fitkit](https://github.com/benredrew/fitkit): physical fit-test gauges.
- [Prusa CLI Preview](https://github.com/benredrew/prusa-cli-preview):
  validated PrusaSlicer BG-code with printer previews.

Aquarium, Oil Shelf, and future projects are separate repositories. They may
use these tools, but Toolbox never downloads or depends on them.

## Install

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
git clone https://github.com/benredrew/toolbox.git
cd toolbox
./install
./toolbox doctor
```

`install` creates one Python 3.12 environment from the committed `uv.lock`.
It also installs a safe `~/.local/bin/toolbox` shim (without replacing an
unrelated command), so projects can invoke the pinned runtime by command
rather than reaching into this checkout's `.venv`.
`doctor` checks the three installed tools, the CAD runtime, PrusaSlicer,
ImageMagick, and the local PrusaSlicer configuration. It does not open a
design project, slice a model, or touch USB media.

For PrusaSlicer support, install the stable Flatpak and ImageMagick, then open
PrusaSlicer once to create its configuration and add the printer/filament
presets you intend to use. `./toolbox doctor` reports what remains missing.

## Use

```bash
./toolbox fit cylinder 112
toolbox python path/to/part.py
./toolbox viewer --name lamp-shade
./toolbox slice model.step \
  --printer "Original Prusa MINI & MINI+ Input Shaper" \
  --filament DogPLA --output model.bgcode
```

The viewer prints `CAD_VIEWER_PORT=<port>` when it starts. Export that value
only for the build that should display there; CadKit's named reservation
registry keeps concurrent viewers from being mixed up.

Toolbox does not prescribe how a project stores its parts or specifications.
It is the reusable toolchain beneath those projects.
