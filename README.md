# 🤟 手语识别项目 — Hand Gesture Recognition

基于 **MediaPipe Hands** 的实时手部关键点检测与手势识别系统。

## 功能

- ✅ 摄像头实时手部 21 关键点检测
- ✅ 手势识别：拳头、张开手掌、数字 1-5
- ✅ 指尖高亮 + 手势标签叠加显示
- ✅ 极简个人介绍网页（可直接部署 GitHub Pages）

---

## 一、环境准备

```bash
# 1. 克隆或进入项目目录
cd "d:/my web"

# 2. 创建虚拟环境（推荐，避免依赖冲突）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

## 二、运行手部识别 Demo

```bash
python hand_gesture_demo.py
```

- 按 **Q** 键退出
- 按 **S** 键截图保存

> 如果提示找不到摄像头，检查摄像头是否被其他应用占用。

---

## 三、GitHub Pages 部署网页

### 第 1 步：创建 GitHub 仓库

1. 打开 [github.com](https://github.com)，登录你的账号
2. 点击右上角 **+** → **New repository**
3. 仓库名填 `hand-gesture-recognition`（或任意名称）
4. 选择 **Public**（公开）
5. 不要勾选 "Add a README file"（我们已有）
6. 点击 **Create repository**

### 第 2 步：推送代码到 GitHub

```bash
# 在项目目录下执行：
cd "d:/my web"

git init
git add .
git commit -m "init: hand gesture recognition project"

# 替换为你的 GitHub 用户名
git remote add origin https://github.com/你的用户名/hand-gesture-recognition.git
git branch -M main
git push -u origin main
```

### 第 3 步：开启 GitHub Pages

1. 打开你的仓库页面 → 点击 **Settings** 标签
2. 左侧菜单点击 **Pages**（在 "Code and automation" 下面）
3. **Source** 选择 **Deploy from a branch**
4. **Branch** 选择 `main`，文件夹选择 `/ (root)`
5. 点击 **Save**
6. 等待 1-2 分钟，页面顶部会出现你的网址：

```
✅ https://你的用户名.github.io/hand-gesture-recognition/
```

### 第 4 步（可选）：绑定自定义域名

在 Settings → Pages → Custom domain 中填入你的域名即可。

---

## 四、嵌入演示视频到网页

### 方式 A：上传到 YouTube（推荐）

1. 录屏 → 上传到 YouTube（设为公开/不公开列出）
2. 在 YouTube 视频下点击 **分享** → **嵌入**
3. 复制 `<iframe>` 代码
4. 替换 `index.html` 中 `<div class="video-wrapper">` 里的占位内容

```html
<div class="video-wrapper">
    <iframe
        width="100%" height="100%"
        src="https://www.youtube.com/embed/你的视频ID"
        title="手语识别演示"
        frameborder="0"
        allowfullscreen
        style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;">
    </iframe>
</div>
```

### 方式 B：视频文件放仓库

1. 把录好的 `.mp4` 文件放到项目根目录
2. 替换占位内容为：

```html
<div class="video-wrapper">
    <video controls style="position:absolute;top:0;left:0;width:100%;height:100%;">
        <source src="demo.mp4" type="video/mp4">
    </video>
</div>
```

---

## 五、项目结构

```
hand-gesture-recognition/
├── hand_gesture_demo.py    # 主程序：关键点检测 + 手势识别
├── requirements.txt         # Python 依赖清单
├── index.html               # 个人主页（GitHub Pages 入口）
└── README.md                # 本文件
```

---

## 六、技术栈

| 组件 | 技术 |
|------|------|
| 手部检测 | MediaPipe Hands (Google) |
| 图像处理 | OpenCV (cv2) |
| 手势分类 | 几何规则（指尖-Joint 距离比） |
| 网页展示 | 纯 HTML + CSS（无框架） |
| 部署 | GitHub Pages |

---

## 七、常见问题

<details>
<summary><b>摄像头打不开？</b></summary>

- Windows：检查隐私设置 → 相机 → 允许桌面应用访问相机
- 确认没有其他应用占用摄像头
- 尝试将 `cv2.VideoCapture(0)` 改为 `cv2.VideoCapture(1)`
</details>

<details>
<summary><b>MediaPipe 安装失败？</b></summary>

```bash
pip install mediapipe --upgrade
```
如果仍然失败，尝试：
```bash
pip install mediapipe==0.10.9
```
</details>

<details>
<summary><b>手势识别不准？</b></summary>

- 调整 `hand_gesture_demo.py` 中的 `threshold` 参数（`is_finger_extended` 默认为 1.15）
- 确保手部在光线充足的环境下，背景尽量干净
- 手部离摄像头 30-60cm 效果最佳
</details>

---

## License

MIT — 自由使用和修改
