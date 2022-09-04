# Examples

**NOTE: These examples are deprecated and may not work with the
latest version of moderngl**

You can use your favorite window with ModernGL.

> Missing?<br>Write an [issue](https://github.com/cprogrammer1994/ModernGL/issues).

If you use ModernGL with a different window or you have an awesome example then please share it!

## Requirements

The examples depend on other modules please read the README files in the subfolders.

Most of the examples depend on the following modules:

- ModernGL _(obviously)_
- Pyrr _(matrix multiplication)_
- Pillow _(loading textures)_
- numpy _(working with arrays)_

It is reccommanded to install these before running the examples.

```sh
pip install moderngl Pyrr Pillow numpy
```

Don't forget to install the module for window support.
Only one per subfolder is enough but you can install all of them with the following commands.

```sh
pip install PyQt5
pip install pyglet
pip install pygame
pip install kivy kivy.deps.sdl2 kivy.deps.glew
pip install PyOpenGL PyOpenGL_accelerate
pip install GLWindow
pip install PySDL2
```

## Contents

- [GLUT](GLUT)
  - [01_hello_world](GLUT/01_hello_world.py)
  - [02_uniforms_and_attributes](GLUT/02_uniforms_and_attributes.py)
  - [03_alpha_blending](GLUT/03_alpha_blending.py)
  - [04_textures](GLUT/04_textures.py)
  - [perspective_projection](GLUT/perspective_projection.py)
  - [window_coordinates](GLUT/window_coordinates.py)

- [GLWindow](GLWindow)
  - [01_hello_world](GLWindow/01_hello_world.py)
  - [02_uniforms_and_attributes](GLWindow/02_uniforms_and_attributes.py)
  - [03_alpha_blending](GLWindow/03_alpha_blending.py)
  - [04_textures](GLWindow/04_textures.py)
  - [05_perspective_projection](GLWindow/05_perspective_projection.py)
  - [05_perspective_projection_using_numpy](GLWindow/05_perspective_projection_using_numpy.py)
  - [julia_fractal](GLWindow/julia_fractal.py)
  - [particle_system](GLWindow/particle_system.py)
  - [particle_system_2](GLWindow/particle_system_2.py)
  - [pillow_font](GLWindow/pillow_font.py)
  - [using_texture3d](GLWindow/using_texture3d.py)
  - [perspective_projection](GLWindow/perspective_projection.py)
  - [window_coordinates](GLWindow/window_coordinates.py)

- [Kivy](Kivy)
  - [01_hello_world](Kivy/01_hello_world.py)
  - [perspective_projection](Kivy/perspective_projection.py)
  - [window_coordinates](Kivy/window_coordinates.py)

- [pygame](pygame)
  - [01_hello_world](pygame/01_hello_world.py)
  - [perspective_projection](pygame/perspective_projection.py)
  - [window_coordinates](pygame/window_coordinates.py)

- [pyglet](pyglet)
  - [01_hello_world](pyglet/01_hello_world.py)
  - [02_uniforms_and_attributes](pyglet/02_uniforms_and_attributes.py)
  - [03_alpha_blending](pyglet/03_alpha_blending.py)
  - [04_textures](pyglet/04_textures.py)
  - [perspective_projection](pyglet/perspective_projection.py)
  - [window_coordinates](pyglet/window_coordinates.py)

- [PyQt5](PyQt5)
  - [01_hello_world](PyQt5/01_hello_world.py)
  - [02_uniforms_and_attributes](PyQt5/02_uniforms_and_attributes.py)
  - [03_alpha_blending](PyQt5/03_alpha_blending.py)
  - [04_textures](PyQt5/04_textures.py)
  - [05_perspective_projection](PyQt5/05_perspective_projection.py)
  - [perspective_projection](PyQt5/perspective_projection.py)
  - [window_coordinates](PyQt5/window_coordinates.py)

- [PyQt5](PySDL2)
  - soon

- [tkinter](tkinter)
  - [01_hello_world](tkinter/01_hello_world.py)
  - [colors](tkinter/colors.py)

- [standalone](standalone)
  - [01_hello_world](standalone/01_hello_world.py)
  - [render_to_pillow_image](standalone/render_to_pillow_image.py)
  - [render_to_pillow_image_multisample](standalone/render_to_pillow_image_multisample.py)
  - [perspective_projection](standalone/perspective_projection.py)
  - [window_coordinates](standalone/window_coordinates.py)

