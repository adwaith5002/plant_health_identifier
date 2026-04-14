import glob, os, numpy as np
from PIL import Image

np.random.seed(0)

def load_images(folder):
    files = glob.glob(os.path.join(folder, "*.png"))
    imgs = []
    for p in files:
        try:
            imgs.append(np.asarray(Image.open(p).convert("RGB"), dtype=np.float32)/255.0)
        except: pass
    return imgs

def features_from_img(rgb):
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    feats = [r.mean(), g.mean(), b.mean(), r.std(), g.std(), b.std()]
    mx = np.maximum(np.maximum(r,g), b); mn = np.minimum(np.minimum(r,g), b)
    c = mx - mn
    v = mx
    s = np.where(mx>1e-8, c/(mx+1e-12), 0.0)
    feats += [s.mean(), v.mean()]
    green_dom = g - np.maximum(r,b)
    green_score = np.maximum(green_dom - 0.03, 0).mean()
    white_ratio = ((s <= 0.30) & (v >= 0.70)).mean()
    feats += [green_score, white_ratio]
    return np.array(feats, dtype=np.float32)  # 10-dim

def make_dataset(root="dataset"):
    X, y = [], []
    for cls, label in [("healthy",0), ("malnourished",1)]:
        for im in load_images(os.path.join(root, cls)):
            X.append(features_from_img(im)); y.append(label)
    X = np.stack(X); y = np.array(y, dtype=np.float32)
    idx = np.arange(len(y)); np.random.shuffle(idx)
    return X[idx], y[idx]

def train_logreg(X, y, lr=0.05, steps=4000, l2=1e-3):
    mu = X.mean(axis=0); sigma = X.std(axis=0)+1e-8
    Z = (X - mu)/sigma
    w = np.zeros(Z.shape[1], dtype=np.float32); b = 0.0
    for t in range(steps):
        z = Z @ w + b
        p = 1/(1+np.exp(-z))
        grad_w = (Z.T @ (p - y))/len(y) + l2*w
        grad_b = np.mean(p - y)
        w -= lr*grad_w; b -= lr*grad_b
        if (t+1) % 500 == 0:
            eps=1e-8
            loss = -np.mean(y*np.log(p+eps)+(1-y)*np.log(1-p+eps)) + 0.5*l2*np.sum(w*w)
            acc  = np.mean(((p>0.5).astype(np.float32)==y))
            print(f"step {t+1}: loss={loss:.4f} acc={acc:.3f}")
    return w, b, mu, sigma

if __name__=="__main__":
    X,y = make_dataset("dataset")
    if len(y) < 20:
        raise SystemExit("Not enough samples. Collect ~50+ per class.")
    w,b,mu,sigma = train_logreg(X,y)
    np.savez("plant_color_model.npz", w=w, b=b, mu=mu, sigma=sigma)
    print("Saved -> plant_color_model.npz")
