import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--exr_path', type=str, default='mitsuba_scene', help='exr_path')
args = parser.parse_args()

hdr = cv2.imread(args.exr_path + '.exr', -1)
# Simply clamp values to a 0-1 range for tone-mapping
ldr = np.clip(hdr, 0, 1)
# Color space conversion
ldr = ldr**(1/2.2)
# 0-255 remapping for bit-depth conversion
ldr = 255.0 * ldr
cv2.imwrite(args.exr_path + '.png', ldr)

