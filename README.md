# Simple 3D Graphics Engine
A simple 3D graphics engine designed to serve as a tool for proof-of-concept algorithms

This is an attempt to simplify the core functions of t

Maybe check the following projects for inspiration:

https://github.com/ubuntunux/PyEngine3D

## High Performance Computing Sources
- https://www.taichi-lang.org/ (Very interesting)
- https://www.ray.io/
- https://numba.pydata.org/
- https://www.dask.org/

## Gizmo sources
- https://github.com/john-chapman/im3d
- https://github.com/CedricGuillemet/ImGuizmo


## Python 3D graphics sources
https://github.com/eth-ait/aitviewer
https://github.com/mmatl/pyrender
https://github.com/pygfx/pygfx
https://github.com/3b1b/manim
https://github.com/eliemichel/Python3dViewer


## Insights on current engine inner workings
- WHen node's translation/rotation/scale is changed via
the setter, it sets the translation to None, and if None
when requested via a getter, it recalculates it just in time.
This is a flexible solution, but not a very efficient one.


## Widget TODOs

### Column
- [ ] Add something here

### Row
- [x] fix width
- [ ] Draw background

### Text Field
- [ ] Allocate memory for text (use max length)

### Text Multi-line Field
- [ ] Allocate memory for text (use max length)
- [ ] Implement rendering on multiple lines
- [ ] Read about real-time text editing  

### Button
- [ ] Change text on buttons dynamically
- [x] Draw background

