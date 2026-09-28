from collections import deque
from dataclasses import dataclass
import numpy as np

@dataclass
class Command:
    direction: str
    magnitude: float
    error: float
    gain: float

class SensorFusion:
    def __init__(self, camera_weight=0.6):
        self.cw = camera_weight
    def fuse(self, camera_speed, imu_speed):
        return self.cw*camera_speed + (1-self.cw)*imu_speed

class AdaptiveController:
    def __init__(self, target=1.0, history=6):
        self.target = target
        self.errors = deque(maxlen=history)
    def update(self, speed):
        err = (speed-self.target)/self.target
        self.errors.append(err)
        if len(self.errors) < 3:
            gain = 1.0
        else:
            recent = np.mean(np.abs(list(self.errors)[-2:]))
            older = np.mean(np.abs(list(self.errors)[:-2]))
            gain = 1.25 if recent >= older else 0.80
        magnitude = float(np.clip(abs(err)*gain, 0, 1))
        if abs(err) < 0.05:
            direction = "hold"
        elif err > 0:
            direction = "slow_down"
        else:
            direction = "speed_up"
        return Command(direction, magnitude, float(err), float(gain))

def visual(cmd):
    symbol = {"speed_up":"↑", "slow_down":"↓", "hold":"✓"}[cmd.direction]
    print(f"  visual: {symbol} strength={cmd.magnitude:.2f}")

def auditory(cmd):
    tone = {"speed_up":"high tone", "slow_down":"low tone", "hold":"confirmation tone"}[cmd.direction]
    print("  audio :", tone)

def haptic(cmd):
    print(f"  haptic: vibration={cmd.magnitude:.2f}")

rng = np.random.default_rng(4)
target = 1.0
human_state = 0.72
fusion = SensorFusion(0.6)
controller = AdaptiveController(target)

history = []
for trial in range(1, 11):
    camera = human_state + rng.normal(0, 0.025)
    imu = human_state + rng.normal(0, 0.040)
    estimated = fusion.fuse(camera, imu)
    cmd = controller.update(estimated)

    print(f"\nTrial {trial}: camera={camera:.3f} imu={imu:.3f} estimated={estimated:.3f}")
    print("  controller:", cmd)
    visual(cmd); auditory(cmd); haptic(cmd)
    history.append(abs(cmd.error))

    correction = 0.30*cmd.magnitude
    if cmd.direction == "speed_up":
        human_state += correction
    elif cmd.direction == "slow_down":
        human_state -= correction
    human_state += rng.normal(0, 0.015)

print("\ninitial abs error:", round(history[0],3))
print("final abs error  :", round(history[-1],3))
print("improvement      :", round(history[0]-history[-1],3))
