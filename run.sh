#!/bin/bash
set -e
pip3 install pillow qrcodegen
python3 pairwise_qr.py
brew install imagemagick
montage -tile 5x0 -geometry +5+5 [a-n].png transparencies.png
