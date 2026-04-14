# controller: plant_identifier.py
from controller import Robot
import os, math

TIME_STEP = 64
robot = Robot()

cam = robot.getDevice("weedCam"); cam.enable(TIME_STEP)
water_led = robot.getDevice("waterLED"); pesticide_led = robot.getDevice("pesticideLED")
left = robot.getDevice("left wheel"); right = robot.getDevice("right wheel")
left.setPosition(float('inf')); right.setPosition(float('inf'))
left.setVelocity(0.0); right.setVelocity(0.0)

CRUISE_SPEED=3.0; FAST_FWD_SPEED=4.5; SLOW_TURN_SPEED=2.0
STOP_EVERY_STEPS=10; ANALYZE_HOLD_STEPS=6; ACTION_STEPS=20
ESCAPE_FWD_STEPS=18; ESCAPE_TURN_STEPS=12
ROI_FRAC=0.70; FOLIAGE_TOP_FRAC=0.10; FOLIAGE_BOTTOM_FRAC=0.70
GREEN_MARGIN=0.03; WHITE_SAT_MAX=0.30; WHITE_VAL_MIN=0.70
WHITE_RATIO_MIN=0.10; GREEN_SCORE_MIN=0.04
MAX_WHEEL=12.3

def clamp(v,lo,hi): return max(lo,min(hi,v))
def set_velocity(l,r=None):
    if r is None: r=l
    left.setVelocity(clamp(l,-MAX_WHEEL,MAX_WHEEL))
    right.setVelocity(clamp(r,-MAX_WHEEL,MAX_WHEEL))
def led_off(): water_led.set(0); pesticide_led.set(0)

try:
    import numpy as np; _NP=True
except Exception:
    _NP=False; np=None

MODEL=None
if _NP and os.path.exists("plant_color_model.npz"):
    z=np.load("plant_color_model.npz")
    MODEL={"w":z["w"],"b":float(z["b"]),"mu":z["mu"],"sigma":z["sigma"]}
    print("[model] loaded plant_color_model.npz")
else:
    print("[model] not found -> heuristic fallback")

def _center_roi_xywh(W,H,frac):
    w=int(W*frac); h=int(H*frac)
    return (W-w)//2,(H-h)//2,w,h
def _foliage_slice(y0,h,H):
    top=int(max(0,(FOLIAGE_TOP_FRAC*H)-y0))
    bot=int(min(h,(FOLIAGE_BOTTOM_FRAC*H)-y0))
    return (0,h) if bot<=top else (top,bot)

def _rgb_to_sv(r,g,b):
    mx=np.maximum(np.maximum(r,g),b); mn=np.minimum(np.minimum(r,g),b)
    c=mx-mn; v=mx; s=np.where(mx>1e-8,c/(mx+1e-12),0.0); return s,v

def _center_crop_rgb():
    arr=np.asarray(cam.getImageArray(),dtype=np.uint8)            # BGRA
    H,W,_=arr.shape
    x0,y0,w,h=_center_roi_xywh(W,H,ROI_FRAC)
    top,bot=_foliage_slice(y0,h,H)
    crop=arr[y0+top:y0+bot, x0:x0+w, [2,1,0]]                    # RGB
    return crop

def _features_from_roi(rgb):
    r=rgb[:,:,0].astype(np.float32)/255.0
    g=rgb[:,:,1].astype(np.float32)/255.0
    b=rgb[:,:,2].astype(np.float32)/255.0
    feats=[r.mean(), g.mean(), b.mean(), r.std(), g.std(), b.std()]
    s,v=_rgb_to_sv(r,g,b)
    feats += [s.mean(), v.mean()]
    green_dom=g-np.maximum(r,b)
    green_score=np.maximum(green_dom-GREEN_MARGIN,0).mean()
    white_ratio=((s<=WHITE_SAT_MAX)&(v>=WHITE_VAL_MIN)).mean()
    feats += [green_score, white_ratio]
    return np.array(feats, dtype=np.float32)

def predict_model():
    if not MODEL: return None
    crop=_center_crop_rgb()
    x=_features_from_roi(crop)
    z=(x-MODEL["mu"])/(MODEL["sigma"]+1e-8)
    s=float(z.dot(MODEL["w"])+MODEL["b"])
    p=1.0/(1.0+math.exp(-s))
    return ("MALNOURISHED" if p>=0.6 else "HEALTHY", p)

def predict_heuristic():
    crop=_center_crop_rgb()
    r,g,b=crop[:,:,0].mean()/255.0, crop[:,:,1].mean()/255.0, crop[:,:,2].mean()/255.0
    s,v=_rgb_to_sv(crop[:,:,0]/255.0, crop[:,:,1]/255.0, crop[:,:,2]/255.0)
    white_ratio=((s<=WHITE_SAT_MAX)&(v>=WHITE_VAL_MIN)).mean()
    green_score=np.maximum(crop[:,:,1]/255.0 - np.maximum(crop[:,:,0]/255.0, crop[:,:,2]/255.0) - GREEN_MARGIN, 0).mean()
    if white_ratio>=WHITE_RATIO_MIN: return "MALNOURISHED", 0.6
    if green_score>=GREEN_SCORE_MIN or (g>r and g>b): return "HEALTHY", 0.6
    return "UNKNOWN", 0.5

print("Controller: MODEL + heuristic fallback")
STATE="MOVE"; timer=0; steps=0; led_off()

while robot.step(TIME_STEP) != -1:
    if STATE=="MOVE":
        set_velocity(CRUISE_SPEED); steps+=1
        if steps>=STOP_EVERY_STEPS:
            steps=0; set_velocity(0.0); timer=ANALYZE_HOLD_STEPS
            STATE="ANALYZE_PRIME"; led_off(); print("🔎 analyze...")

    elif STATE=="ANALYZE_PRIME":
        set_velocity(0.0); timer-=1
        if timer<=0: STATE="ANALYZE"

    elif STATE=="ANALYZE":
        set_velocity(0.0)
        out=predict_model()
        if out is None:
            decision, conf = predict_heuristic()
            print(f"[heur] → {decision} (conf≈{conf:.2f})")
        else:
            decision, conf = out
            print(f"[model] → {decision} (p={conf:.2f})")

        if decision=="HEALTHY":
            water_led.set(1); pesticide_led.set(0)
            timer=ACTION_STEPS; STATE="WATERING"; print("✅ Water")
        elif decision=="MALNOURISHED":
            water_led.set(0); pesticide_led.set(1)
            timer=ACTION_STEPS; STATE="SPRAYING"; print("⚠️ Pesticide")
        else:
            led_off(); timer=ESCAPE_FWD_STEPS; STATE="ESCAPE_FWD"; print("🤔 Skip")

    elif STATE=="WATERING":
        set_velocity(0.0); timer-=1
        if timer<=0: led_off(); timer=ESCAPE_FWD_STEPS; STATE="ESCAPE_FWD"; print("➡️ done")

    elif STATE=="SPRAYING":
        set_velocity(0.0); timer-=1
        if timer<=0: led_off(); timer=ESCAPE_FWD_STEPS; STATE="ESCAPE_FWD"; print("➡️ done")

    elif STATE=="ESCAPE_FWD":
        set_velocity(FAST_FWD_SPEED, FAST_FWD_SPEED); timer-=1
        if timer<=0: timer=ESCAPE_TURN_STEPS; STATE="ESCAPE_SPIN"; print("↪️ spin")

    elif STATE=="ESCAPE_SPIN":
        set_velocity(SLOW_TURN_SPEED, -SLOW_TURN_SPEED); timer-=1
        if timer<=0: led_off(); STATE="MOVE"; print("➡️ resume")
