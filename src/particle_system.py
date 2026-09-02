import cv2
import random
import math
import time

class Particle:
    def __init__(self, x, y, kind):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.vx = random.uniform(-45,45)
        self.vy = random.uniform(-90,-30)
        self.life = random.uniform(0.65,1.4)
        self.age = 0.0
        self.size = random.randint(3,8)

class ParticleSystem:
    def __init__(self, max_particles=60):
        self.max_particles = int(max_particles)
        self.items = []
        self.last = time.perf_counter()

    def emit(self, x, y, kind, count=2):
        if kind in (None, "", "none"):
            return
        for _ in range(count):
            if len(self.items) >= self.max_particles:
                break
            self.items.append(Particle(x, y, kind))

    def update_draw(self, frame):
        now = time.perf_counter()
        dt = min(now-self.last, 0.05)
        self.last = now
        h, w = frame.shape[:2]
        alive = []
        for p in self.items:
            p.age += dt
            if p.age >= p.life:
                continue
            p.x += p.vx*dt
            p.y += p.vy*dt
            p.vy += 80*dt
            alpha = 1.0-p.age/p.life
            x = int(p.x)
            y = int(p.y)
            if 0 <= x < w and 0 <= y < h:
                if p.kind == "heart":
                    r = max(2, int(p.size*alpha))
                    cv2.circle(frame, (x-r//2,y), r, (180,80,255), -1, cv2.LINE_AA)
                    cv2.circle(frame, (x+r//2,y), r, (180,80,255), -1, cv2.LINE_AA)
                    pts = [(x-r,y),(x+r,y),(x,y+2*r)]
                    cv2.fillConvexPoly(frame, __import__("numpy").array(pts, dtype="int32"), (180,80,255))
                elif p.kind == "flower":
                    r = max(2, int(p.size*alpha))
                    for a in range(0,360,72):
                        px = x + int(math.cos(math.radians(a))*r)
                        py = y + int(math.sin(math.radians(a))*r)
                        cv2.circle(frame, (px,py), r, (220,150,255), -1, cv2.LINE_AA)
                    cv2.circle(frame, (x,y), max(1,r//2), (80,220,255), -1, cv2.LINE_AA)
                else:
                    r = max(1, int(p.size*alpha))
                    cv2.line(frame, (x-r,y), (x+r,y), (255,255,255), 1, cv2.LINE_AA)
                    cv2.line(frame, (x,y-r), (x,y+r), (255,255,255), 1, cv2.LINE_AA)
            alive.append(p)
        self.items = alive
