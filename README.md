# 多项目代码仓库

这个仓库现在按项目拆分管理，每个项目都可独立开发、独立运行、独立编写说明。

## 项目目录

- `projects/macro_logic`：宏观资产传导推演系统
- `projects/property_tender`：住宅物业投标报价决策系统

## 如何运行

### 1) 宏观资产传导推演系统

```bash
cd projects/macro_logic
pip install -r requirements.txt
streamlit run app.py
```

### 2) 住宅物业投标报价决策系统

```bash
cd projects/property_tender
pip install -r requirements.txt
streamlit run tender_app.py
```

## 后续建议

- 每个项目单独维护自己的 README、依赖和变更说明。
- 若后续项目继续增加，按同样方式放到 `projects/` 下即可。
