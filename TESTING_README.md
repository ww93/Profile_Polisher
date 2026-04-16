# 运行测试 README

本文档说明如何在本地运行 **Profile Polisher** 的后端、前端与接口联调测试。

## 1. 环境准备

- Python 3.10+
- Node.js 18+
- npm 9+

可选（如果要测试 Parseur 拉取）：

- `PARSEUR_API_TOKEN`
- `PARSEUR_MAILBOX_ID`

---

## 2. 后端启动与基础检查

在仓库根目录执行：

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

默认地址：`http://localhost:8000`

### 2.1 健康检查

```bash
curl http://localhost:8000/health
```

期望返回：

```json
{"status":"ok"}
```

---

## 3. 前端启动

在新终端执行：

```bash
cd frontend
npm install
npm run dev
```

默认地址：`http://localhost:5173`

---

## 4. 接口测试（不依赖 Parseur）

### 4.1 纯文本简历 + JD

```bash
curl -X POST http://localhost:8000/analyze \
  -F 'jd_text=We need Python, Docker, SQL experience.' \
  -F 'resume_text=Built backend services using Python and SQL. Project: order platform.'
```

验证点：
- 返回 `match.overall_score`
- 返回 `optimizations` 与 `interview_questions`
- 返回 `comparison.has_previous=false`

### 4.2 PDF/DOCX 上传

```bash
curl -X POST http://localhost:8000/analyze \
  -F 'jd_text=Looking for React and Node engineers.' \
  -F 'resume_file=@/ABSOLUTE/PATH/resume.pdf'
```

或：

```bash
curl -X POST http://localhost:8000/analyze \
  -F 'jd_text=Looking for React and Node engineers.' \
  -F 'resume_file=@/ABSOLUTE/PATH/resume.docx'
```

验证点：
- PDF/DOCX 均可解析
- 不支持格式（如 `.txt` 文件上传）时返回 400

---

## 5. 追问补充（复用 `/analyze`）

先做第一轮请求，保存响应为 `result_v1.json`。

第二轮在同一接口附加补充信息：

```bash
curl -X POST http://localhost:8000/analyze \
  -F 'jd_text=We need Python, Docker, SQL experience.' \
  -F 'resume_text=Built backend services using Python and SQL. Project: order platform.' \
  -F 'supplement_json={"candidate_context":"Led 4 engineers","job_constraints":"Need onboarding in 30 days","optimization_goal":"Highlight system reliability","focus_sections":["projects"]}' \
  -F 'previous_result_json=<把 result_v1.json 内容压成单行再粘贴>'
```

验证点：
- `supplement_applied` 有值
- `comparison.has_previous=true`
- 返回 `score_delta` / `added_strengths` / `removed_gaps`

---

## 6. Parseur 集成测试（可选）

配置环境变量后：

```bash
export PARSEUR_API_TOKEN=your_token
export PARSEUR_MAILBOX_ID=your_mailbox
```

然后：

```bash
curl -X POST http://localhost:8000/analyze \
  -F 'jd_text=Need Python and FastAPI.' \
  -F 'parseur_document_id=<document_id>'
```

验证点：
- Parseur 可用时，后端可拉取文档文本
- Parseur 不可用时，可回退到 `resume_text` 或 `resume_file`

---

## 7. 常见问题排查

1. `ModuleNotFoundError: fastapi`
   - 说明未安装后端依赖，重新执行 `pip install -r requirements.txt`

2. `vite: not found`
   - 说明前端依赖未安装，执行 `cd frontend && npm install`

3. npm 403 / 网络受限
   - 说明当前环境无法访问 npm registry，需要切换网络或镜像源

4. `Unsupported file type. Please upload PDF or DOCX.`
   - 上传文件后缀不受支持，请改用 `.pdf` 或 `.docx`

---

## 8. 最小回归清单（建议每次改动后执行）

- [ ] `/health` 正常
- [ ] 文本模式 `/analyze` 正常
- [ ] PDF 上传 `/analyze` 正常
- [ ] DOCX 上传 `/analyze` 正常
- [ ] 追问补充返回 comparison 结果
- [ ] 前端可加载并完成一轮提交


## 9. LLM（BYOK）测试

你可以在同一接口传入 `llm_config_json` 触发 LLM 分析：

```bash
curl -X POST http://localhost:8000/analyze \
  -F 'jd_text=Need Python and FastAPI.' \
  -F 'resume_text=Built API services with Python and FastAPI.' \
  -F 'llm_config_json={"api_key":"<YOUR_KEY>","base_url":"https://api.openai.com/v1","model":"gpt-4.1-mini","temperature":0.2}'
```

验证点：
- 返回结构与普通模式一致
- 内容通常比规则模式更细致（strengths/gaps/evidence）
- key 不存储在后端，仅用于本次请求
