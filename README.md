# 宏观资产传导推演系统

一个基于 Streamlit 的宏观事件-资产传导推演工具，支持：

- 单场景推演
- 双场景对比
- 传导链置信度微调
- Markdown 简报导出

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 长期部署（免费，不上架 App Store）

推荐使用 Streamlit Community Cloud，生成长期 HTTPS 链接。

### 1. 上传到 GitHub

1. 在 GitHub 新建仓库（例如：`macro-compass`）。
2. 在项目目录执行：

```bash
git init
git add .
git commit -m "feat: initial streamlit macro compass"
git branch -M main
git remote add origin <你的仓库地址>
git push -u origin main
```

### 2. 部署到 Streamlit Community Cloud

1. 打开 https://share.streamlit.io/
2. 使用 GitHub 登录并授权。
3. 点击 `New app`，选择你的仓库与分支：
   - Repository: 你的仓库
   - Branch: `main`
   - Main file path: `app.py`
4. 点击 `Deploy`。

部署后会得到一个长期可访问的 HTTPS 链接（例如 `https://xxxx.streamlit.app`）。

### 3. iPhone 变成“桌面 App”

1. 在 iPhone Safari 打开部署链接。
2. 点底部 `分享`。
3. 选择 `添加到主屏幕`。

完成后会出现桌面图标，点击即可像 App 一样打开。

## 说明

- 不需要苹果开发者付费账号。
- 这不是原生 iOS App，而是 Web App（PWA 风格体验）。
- 只要 Streamlit Cloud 运行正常，手机可随时访问。
