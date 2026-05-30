"""
自动化测试：模拟不同手势的手部关键点，验证 0-5 根手指计数是否准确。
不依赖摄像头，纯逻辑验证。
"""
import math
from typing import Tuple, List

# ============================================================
#  从 hand_gesture_demo.py 复制的核心逻辑（保持完全一致）
# ============================================================

FINGER_ANGLE_THRESHOLD = 155.0
THUMB_ANGLE_THRESHOLD  = 145.0
THUMB_WRIST_RATIO      = 0.85

FINGER_DEFS = {
    "thumb":  {"mcp": 2,  "pip": 3,  "tip": 4},
    "index":  {"mcp": 5,  "pip": 6,  "tip": 8},
    "middle": {"mcp": 9,  "pip": 10, "tip": 12},
    "ring":   {"mcp": 13, "pip": 14, "tip": 16},
    "pinky":  {"mcp": 17, "pip": 18, "tip": 20},
}

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def angle_at_joint(a, b, c):
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(ba[0], ba[1])
    mag_bc = math.hypot(bc[0], bc[1])
    if mag_ba * mag_bc < 0.0001:
        return 0.0
    cos_val = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return math.degrees(math.acos(cos_val))

def is_finger_open(coords, finger_name):
    fd = FINGER_DEFS[finger_name]
    mcp = coords[fd["mcp"]]
    pip = coords[fd["pip"]]
    tip = coords[fd["tip"]]
    joint_angle = angle_at_joint(mcp, pip, tip)
    if finger_name == "thumb":
        wrist = coords[0]
        d_tip_wrist = distance(tip, wrist)
        d_mcp_wrist = distance(mcp, wrist)
        wrist_ratio = d_tip_wrist / (d_mcp_wrist + 0.001)
        is_open = joint_angle > THUMB_ANGLE_THRESHOLD and wrist_ratio > THUMB_WRIST_RATIO
    else:
        is_open = joint_angle > FINGER_ANGLE_THRESHOLD
    return is_open, joint_angle

def count_fingers(coords):
    states = {name: is_finger_open(coords, name) for name in FINGER_DEFS}
    count = sum(v[0] for v in states.values())
    return count, states

# ============================================================
#  模拟数据生成
# ============================================================

def generate_open_palm(width=640, height=480):
    """张开手掌：5根手指全部伸直"""
    w, h = width / 2, height / 2
    return [
        (w, h + 100),                    # 0  WRIST
        (w - 30, h + 10),                # 1  THUMB_CMC
        (w - 70, h - 10),                # 2  THUMB_MCP
        (w - 90, h - 50),                # 3  THUMB_IP
        (w - 100, h - 100),              # 4  THUMB_TIP (extended)
        (w - 30, h - 60),                # 5  INDEX_MCP
        (w - 30, h - 120),               # 6  INDEX_PIP
        (w - 30, h - 160),               # 7  INDEX_DIP
        (w - 30, h - 200),               # 8  INDEX_TIP (extended up)
        (w, h - 70),                      # 9  MIDDLE_MCP
        (w, h - 140),                     # 10 MIDDLE_PIP
        (w, h - 190),                     # 11 MIDDLE_DIP
        (w, h - 240),                     # 12 MIDDLE_TIP (extended up)
        (w + 30, h - 60),                 # 13 RING_MCP
        (w + 30, h - 110),                # 14 RING_PIP
        (w + 30, h - 150),                # 15 RING_DIP
        (w + 30, h - 190),                # 16 RING_TIP (extended up)
        (w + 60, h - 40),                 # 17 PINKY_MCP
        (w + 60, h - 80),                 # 18 PINKY_PIP
        (w + 60, h - 110),                # 19 PINKY_DIP
        (w + 60, h - 140),                # 20 PINKY_TIP (extended up)
    ]

def generate_fist(width=640, height=480):
    """握拳：所有手指弯曲"""
    w, h = width / 2, height / 2
    return [
        (w, h + 100),                    # 0  WRIST
        (w - 30, h + 20),                # 1  THUMB_CMC
        (w - 60, h + 10),                # 2  THUMB_MCP (near palm)
        (w - 50, h - 10),                # 3  THUMB_IP (tucked)
        (w - 30, h - 20),                # 4  THUMB_TIP (tucked)
        (w - 30, h - 50),                # 5  INDEX_MCP
        (w - 15, h - 40),                # 6  INDEX_PIP (bent forward)
        (w, h - 20),                      # 7  INDEX_DIP (curling)
        (w, h),                           # 8  INDEX_TIP (tucked in)
        (w, h - 55),                      # 9  MIDDLE_MCP
        (w + 15, h - 45),                 # 10 MIDDLE_PIP (bent)
        (w + 10, h - 20),                 # 11 MIDDLE_DIP
        (w + 5, h),                       # 12 MIDDLE_TIP (tucked)
        (w + 30, h - 45),                 # 13 RING_MCP
        (w + 45, h - 35),                 # 14 RING_PIP (bent)
        (w + 40, h - 15),                 # 15 RING_DIP
        (w + 30, h),                      # 16 RING_TIP (tucked)
        (w + 60, h - 30),                 # 17 PINKY_MCP
        (w + 70, h - 20),                 # 18 PINKY_PIP (bent)
        (w + 65, h - 5),                  # 19 PINKY_DIP
        (w + 55, h + 10),                 # 20 PINKY_TIP (tucked)
    ]

def generate_one(width=640, height=480):
    """数字1：仅食指伸直"""
    coords = generate_fist(width, height)
    # 修改食指：向上伸直
    w, h = width / 2, height / 2
    coords[5] = (w - 30, h - 60)    # INDEX_MCP
    coords[6] = (w - 30, h - 130)   # INDEX_PIP (straight up)
    coords[7] = (w - 30, h - 180)   # INDEX_DIP
    coords[8] = (w - 30, h - 230)   # INDEX_TIP (extended)
    return coords

def generate_two(width=640, height=480):
    """数字2：食指+中指伸直"""
    coords = generate_fist(width, height)
    w, h = width / 2, height / 2
    # 食指伸直
    coords[5] = (w - 30, h - 60)
    coords[6] = (w - 30, h - 130)
    coords[7] = (w - 30, h - 180)
    coords[8] = (w - 30, h - 230)
    # 中指伸直
    coords[9] = (w, h - 70)
    coords[10] = (w, h - 150)
    coords[11] = (w, h - 210)
    coords[12] = (w, h - 260)
    return coords

def generate_three(width=640, height=480):
    """数字3：拇指+食指+中指伸直"""
    coords = generate_fist(width, height)
    w, h = width / 2, height / 2
    # 拇指打开
    coords[1] = (w - 30, h + 10)
    coords[2] = (w - 80, h - 30)
    coords[3] = (w - 110, h - 80)
    coords[4] = (w - 130, h - 130)
    # 食指伸直
    coords[5] = (w - 30, h - 60)
    coords[6] = (w - 30, h - 130)
    coords[7] = (w - 30, h - 180)
    coords[8] = (w - 30, h - 230)
    # 中指伸直
    coords[9] = (w, h - 70)
    coords[10] = (w, h - 150)
    coords[11] = (w, h - 210)
    coords[12] = (w, h - 260)
    return coords

def generate_four(width=640, height=480):
    """数字4：除拇指外4根伸直"""
    coords = generate_fist(width, height)
    w, h = width / 2, height / 2
    # 拇指保持弯曲（拳头状态）
    # 四指全部伸直
    coords[5] = (w - 30, h - 60)
    coords[6] = (w - 30, h - 130)
    coords[8] = (w - 30, h - 230)
    coords[9] = (w, h - 70)
    coords[10] = (w, h - 150)
    coords[12] = (w, h - 260)
    coords[13] = (w + 30, h - 60)
    coords[14] = (w + 30, h - 120)
    coords[16] = (w + 30, h - 200)
    coords[17] = (w + 60, h - 40)
    coords[18] = (w + 60, h - 90)
    coords[20] = (w + 60, h - 150)
    return coords


# ============================================================
#  测试执行
# ============================================================

def run_tests():
    tests = [
        ("Open Palm / Five (5)", generate_open_palm, 5),
        ("Fist (0)",             generate_fist,      0),
        ("One (1)",              generate_one,       1),
        ("Two (2)",              generate_two,       2),
        ("Three (3)",            generate_three,     3),
        ("Four (4)",             generate_four,      4),
    ]

    all_pass = True
    print("=" * 70)
    print(f"{'Gesture':<25} {'Expected':>8} {'Count':>8} {'Angles (T/I/M/R/P)':>30} {'Result':>8}")
    print("-" * 70)

    for name, gen_func, expected in tests:
        coords = gen_func()
        count, states = count_fingers(coords)

        # 获取各手指角度
        angles = []
        for finger_name in ["thumb", "index", "middle", "ring", "pinky"]:
            _, ang = states[finger_name]
            angles.append(f"{ang:.0f}")
        angle_str = "/".join(angles)

        status = "PASS" if count == expected else "FAIL"
        if count != expected:
            all_pass = False

        print(f"{name:<25} {expected:>8} {count:>8} {angle_str:>30} {status:>8}")

    print("-" * 70)
    if all_pass:
        print("ALL TESTS PASSED - 0-5 finger counting is accurate!")
    else:
        print("SOME TESTS FAILED - thresholds need adjustment!")

    return all_pass


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
