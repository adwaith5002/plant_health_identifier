# controller: collect_dataset.py
from controller import Robot
import pathlib, time, numpy as np, imageio

TIME_STEP = 64
robot = Robot()

cam = robot.getDevice("weedCam")
cam.enable(TIME_STEP)

left = robot.getDevice("left wheel")
right = robot.getDevice("right wheel")
left.setPosition(float('inf')); right.setPosition(float('inf'))
left.setVelocity(2.0); right.setVelocity(2.0)

CURRENT_LABEL = "malnourished"   # <-- run once with "healthy", then change to "malnourished"
SAVE_EVERY_STEPS = 6        # ~0.4 s
ROI_FRAC = 0.70             # big center crop

root = (pathlib.Path("dataset") / CURRENT_LABEL)
root.mkdir(parents=True, exist_ok=True)

def center_crop_rgb(cam, frac=0.7):
    # Webots gives BGRA → convert to RGB
    arr = np.asarray(cam.getImageArray(), dtype=np.uint8)  # (H,W,4)
    H, W, _ = arr.shape
    w = int(W*frac); h = int(H*frac)
    x0 = (W - w)//2; y0 = (H - h)//2
    crop = arr[y0:y0+h, x0:x0+w, [2,1,0]]  # RGB
    return crop

step = 0
print(f"[collector] Saving to {root} label={CURRENT_LABEL}")
while robot.step(TIME_STEP) != -1:
    step += 1
    if step % SAVE_EVERY_STEPS == 0:
        crop = center_crop_rgb(cam, ROI_FRAC)
        fn = root / f"{int(time.time()*1000)}.png"
        imageio.imwrite(fn.as_posix(), crop)
        print("saved", fn.name)
