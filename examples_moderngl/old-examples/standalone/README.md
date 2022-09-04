# Standalone examples

Headless rendering

ModernGL examples that can be run on servers.

<img alt="01_hello_world.png" src="https://raw.githubusercontent.com/cprogrammer1994/ModernGL/master/docs/Examples/images/headless.png">

## Requirements

```shell
pip install moderngl Pillow Pyrr numpy
```

## Running examples without a display

```shell
sudo apt-get install xvfb
Xvfb -screen 0 640x480x24 :99 &
export DISPLAY=:99.0
python examples/standalone/01_hellow_world.py
```

## Quick sample (without git clone)

Tested on DigitalOcean's Ubuntu 16.04.2 x64

```shell
sudo apt-get update
sudo apt-get install -y xvfb python3 python3-virtualenv
python3 -m virtualenv --python=python3 venv
source venv/bin/activate
pip install moderngl Pillow Pyrr numpy
Xvfb -screen 0 640x480x24 :99 &
export DISPLAY=:99.0
wget https://raw.githubusercontent.com/cprogrammer1994/ModernGL/master/examples/standalone/01_hello_world.py
python 01_hello_world.py
ls 01_hello_world.png
```

### Using `xvfb-run`

```shell
sudo apt-get update
sudo apt-get install -y xvfb python3 python3-virtualenv
python3 -m virtualenv --python=python3 venv
source venv/bin/activate
pip install moderngl Pillow Pyrr numpy
wget https://raw.githubusercontent.com/cprogrammer1994/ModernGL/master/examples/standalone/01_hello_world.py
xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' python 01_hello_world.py
ls 01_hello_world.png
```

<img width="50%" alt="01_hello_world.png" src="https://raw.githubusercontent.com/cprogrammer1994/ModernGL/master/docs/Examples/images/01_hello_world.png">

## Debugging

```shell
sudo apt-get install mesa-utils
glxinfo | grep OpenGL
```

Please include the result of `glxinfo` in the bug report.
