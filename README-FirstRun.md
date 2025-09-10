# FoodIdentification527

本项目包含 **后端 (FastAPI)** 和 **前端 (React/Vite)**，支持本地运行和开发。

---

## 🚀 环境准备

### 1. 克隆项目
```bash
git clone <仓库地址>
cd FoodIdentification527
```

### 2. 安装依赖

#### 后端 (FastAPI + Python)
进入 `python` 目录，创建并激活 Conda 环境：
```bash
cd python
conda create -n myenv python=3.9 -y
conda activate myenv
```

安装依赖：
```bash
pip install -r requirements.txt
```

#### 前端 (React + Vite)
进入 `client` 目录，安装依赖：
```bash
cd ../client
npm install
```

---

## ▶️ 启动项目

### 启动后端
在 `python` 目录下：
```bash
conda activate myenv
python -m uvicorn main:app --reload
# 如果报错 "command not found: python"，请改用：
# python3 -m uvicorn main:app --reload
```

后端启动后，访问：
- API 文档: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 启动前端
在 `client` 目录下：
```bash
npm run dev
```

前端启动后，访问：
- 前端页面: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## ⚠️ 常见问题

1. **`ArgumentError: activate does not accept more than one argument`**
   - 请确保命令里没有复制注释：
   ```bash
   conda activate myenv
   ```

2. **`zsh: command not found: python`**
   - 请改用：
   ```bash
   python3 -m uvicorn main:app --reload
   ```

3. **端口被占用 (`Address already in use`)**
   - 换一个端口运行：
   ```bash
   python -m uvicorn main:app --reload --port 8001
   ```

---

## 🛠️ 快捷启动脚本（可选）

在 `python` 目录下新建 `run.sh`：

```bash
#!/bin/bash
cd "$(dirname "$0")"
conda activate myenv
python -m uvicorn main:app --reload
```

给脚本执行权限：
```bash
chmod +x run.sh
```

之后只需运行：
```bash
./run.sh
```

---

## 📂 项目结构
```
FoodIdentification527/
│── client/        # 前端 React + Vite
│── python/        # 后端 FastAPI
│   ├── core/
│   ├── dao/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── uploads/
│   ├── utils/
│   ├── db.py
│   ├── jwt.py
│   └── main.py
│── requirements.txt
│── docker-compose.yml (可选)
```

---

## ✅ 总结
- **后端**：进入 `python` → 激活 Conda → `uvicorn` 启动服务  
- **前端**：进入 `client` → `npm run dev` 启动开发服务器  
- 前后端都启动后即可访问项目。
