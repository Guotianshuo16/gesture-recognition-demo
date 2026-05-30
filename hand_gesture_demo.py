"""
手语识别项目 —— MediaPipe Hands 手部关键点检测 + 手势识别
手指判断：关节角度法（∠MCP→PIP→TIP 或 ∠CMC→MCP→TIP）
支持：拳头、张开手掌、数字 1-5
按 Q 退出，按 S 截图保存
"""

import cv2
import mediapipe as mp
import math
from typing import Tuple, List

# ============================================================
#  初始化 MediaPipe Hands
# ============================================================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,              # 最多检测两只手
    model_complexity=1,           # 模型复杂度（0=轻量, 1=完整）
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# ============================================================
#  MediaPipe 手部关键点索引参考
# ============================================================
#  0:  WRIST
#  1:  THUMB_CMC     2:  THUMB_MCP     3:  THUMB_IP      4:  THUMB_TIP
#  5:  INDEX_MCP     6:  INDEX_PIP     7:  INDEX_DIP      8:  INDEX_TIP
#  9:  MIDDLE_MCP   10:  MIDDLE_PIP    11:  MIDDLE_DIP    12:  MIDDLE_TIP
# 13:  RING_MCP     14:  RING_PIP     15:  RING_DIP      16:  RING_TIP
# 17:  PINKY_MCP    18:  PINKY_PIP    19:  PINKY_DIP     20:  PINKY_TIP

# ---- 手指定义：每个手指的 (MCP, PIP, TIP) 索引 ----
FINGER_DEFS = {
    "thumb":  {"mcp": 2,  "pip": 3,  "tip": 4},    # 拇指用 MCP-IP-TIP
    "index":  {"mcp": 5,  "pip": 6,  "tip": 8},
    "middle": {"mcp": 9,  "pip": 10, "tip": 12},
    "ring":   {"mcp": 13, "pip": 14, "tip": 16},
    "pinky":  {"mcp": 17, "pip": 18, "tip": 20},
}

# ---- 伸直/弯曲阈值（度） ----
FINGER_ANGLE_THRESHOLD = 155.0   # 四指：∠MCP-PIP-TIP > 155° 视为伸直
THUMB_ANGLE_THRESHOLD  = 145.0   # 拇指：∠MCP-IP-TIP   > 145° 视为张开
THUMB_WRIST_RATIO      = 0.85    # 拇指：TIP到手腕 / MCP到手腕 > 0.85 辅助判断

# ============================================================
#  工具函数
# ============================================================

def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """计算两点之间的欧氏距离"""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def angle_at_joint(
    a: Tuple[float, float],
    b: Tuple[float, float],
    c: Tuple[float, float]
) -> float:
    """
    计算 ∠ABC，即以 B 为顶点的夹角，返回角度值（0~180°）。
    - 手指完全伸直时接近 180°
    - 手指弯曲时角度变小
    """
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])

    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(ba[0], ba[1])
    mag_bc = math.hypot(bc[0], bc[1])

    if mag_ba * mag_bc < 0.0001:
        return 0.0  # 点重叠，避免除零

    # 限制浮点精度防止 acos 越界
    cos_val = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return math.degrees(math.acos(cos_val))


def landmarks_to_coords(landmarks, width: int, height: int) -> List[Tuple[float, float]]:
    """将归一化的 landmarks 转换为像素坐标"""
    coords = []
    for lm in landmarks.landmark:
        coords.append((lm.x * width, lm.y * height))
    return coords


# ============================================================
#  手指状态判定 —— 关节角度法
# ============================================================

def is_finger_open(
    coords: List[Tuple[float, float]],
    finger_name: str
) -> Tuple[bool, float]:
    """
    用关节角度法判断一根手指是否伸直/张开。
    返回 (是否伸直, 关节角度值)。

    对于食指/中指/无名指/小指：
        ∠MCP → PIP → TIP 的角度 > 155° 表示伸直

    对于拇指：
        - 主判断：∠MCP → IP → TIP 的角度 > 145°
        - 辅助判断：TIP 到手腕距离 / MCP 到手腕距离 > 0.85
    """
    fd = FINGER_DEFS[finger_name]
    mcp = coords[fd["mcp"]]
    pip = coords[fd["pip"]]
    tip = coords[fd["tip"]]

    # 关节角度
    joint_angle = angle_at_joint(mcp, pip, tip)

    if finger_name == "thumb":
        # ---- 拇指：角度 + 手腕距离比（双重保障） ----
        wrist = coords[0]
        d_tip_wrist = distance(tip, wrist)
        d_mcp_wrist = distance(mcp, wrist)
        wrist_ratio = d_tip_wrist / (d_mcp_wrist + 0.001)

        is_open = (
            joint_angle > THUMB_ANGLE_THRESHOLD
            and wrist_ratio > THUMB_WRIST_RATIO
        )
    else:
        # ---- 四指：纯角度判断 ----
        is_open = joint_angle > FINGER_ANGLE_THRESHOLD

    return is_open, joint_angle


def get_all_finger_states(coords: List[Tuple[float, float]]) -> dict:
    """获取所有 5 根手指的状态，返回字典 {finger_name: (is_open, angle)}"""
    return {
        name: is_finger_open(coords, name)
        for name in FINGER_DEFS
    }


# ============================================================
#  手势分类
# ============================================================

def count_fingers(finger_states: dict) -> int:
    """
    纯手指计数：统计 5 根手指中伸直的数量（0~5）。
    不区分具体哪根手指，不做手势分类。
    """
    return sum(state[0] for state in finger_states.values())


# ============================================================
#  摄像头主循环
# ============================================================

def main():
    cap = cv2.VideoCapture(0)  # 打开默认摄像头

    if not cap.isOpened():
        print("[ERROR] Cannot open camera! Check device connection.")
        return

    print("[INFO] Camera opened — Press Q to quit, S to screenshot")

    while True:
        success, frame = cap.read()
        if not success:
            print("[WARN] Failed to read frame")
            break

        # 翻转画面（镜像效果更自然）
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        # 手部关键点检测
        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
                # ---- 绘制关键点连线 ----
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )

                # ---- 手指计数 ----
                coords = landmarks_to_coords(hand_landmarks, w, h)
                finger_states = get_all_finger_states(coords)
                count = count_fingers(finger_states)

                # ---- 手腕上方显示手指数量 ----
                handedness = result.multi_handedness[idx].classification[0].label
                wrist = coords[0]
                text_x = max(int(wrist[0]) - 40, 10)
                text_y = max(int(wrist[1]) - 30, 30)

                # 手指计数标签（绿色加粗大字）
                cv2.putText(
                    frame,
                    f"{handedness}: {count}",
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1.2,
                    (0, 255, 0),
                    3,
                    cv2.LINE_AA,
                )

                # ---- 指尖高亮 + 角度数值标注 ----
                for name, (_, pip_idx, tip_idx) in {
                    "T": (1, 3, 4),   # thumb: CMC-IP-TIP
                    "I": (5, 6, 8),   # index
                    "M": (9, 10, 12), # middle
                    "R": (13, 14, 16),# ring
                    "P": (17, 18, 20),# pinky
                }.items():
                    tx, ty = int(coords[tip_idx][0]), int(coords[tip_idx][1])
                    pip_pos = (int(coords[pip_idx][0]), int(coords[pip_idx][1]))

                    # 指尖实心圆（红色=弯曲，青色=伸直）
                    _, angle = finger_states.get(
                        {"T": "thumb", "I": "index", "M": "middle",
                         "R": "ring", "P": "pinky"}[name],
                        (False, 0)
                    )
                    color = (0, 255, 255) if angle > (THUMB_ANGLE_THRESHOLD if name == "T" else FINGER_ANGLE_THRESHOLD) else (0, 0, 255)
                    cv2.circle(frame, (tx, ty), 10, color, -1)  # 实心圆

                    # 小标签：手指名 + 角度
                    cv2.putText(
                        frame,
                        f"{name}{angle:.0f}",
                        (tx + 12, ty - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA,
                    )

                    # PIP 关节点小圆（白色）
                    cv2.circle(frame, pip_pos, 4, (255, 255, 255), -1)

        # ---- 顶部状态栏 ----
        cv2.putText(
            frame,
            "Hand Gesture Recognition | Q: Quit | S: Screenshot",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow("Hand Gesture Recognition", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("[INFO] Quit")
            break
        elif key == ord("s"):
            filename = f"screenshot_{cv2.getTickCount()}.png"
            cv2.imwrite(filename, frame)
            print(f"[INFO] Screenshot saved: {filename}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
