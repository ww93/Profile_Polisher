import { useMemo, useState } from 'react'

const API_BASE = 'http://localhost:8000'

const defaultSupplement = {
  candidate_context: '',
  job_constraints: '',
  optimization_goal: '',
  focus_sections: [],
}

function App() {
  const [jdText, setJdText] = useState('')
  const [resumeText, setResumeText] = useState('')
  const [resumeFile, setResumeFile] = useState(null)
  const [parseurDocumentId, setParseurDocumentId] = useState('')
  const [supplement, setSupplement] = useState(defaultSupplement)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')

  const comparisonTips = useMemo(() => {
    if (!result?.comparison?.has_previous) return []
    const tips = []
    if (result.comparison.score_delta > 0) {
      tips.push(`匹配分提升 +${result.comparison.score_delta}`)
    } else if (result.comparison.score_delta < 0) {
      tips.push(`匹配分下降 ${result.comparison.score_delta}`)
    } else {
      tips.push('匹配分无变化')
    }
    return tips
  }, [result])

  const setFocusSection = (value, checked) => {
    setSupplement((prev) => {
      const next = new Set(prev.focus_sections)
      if (checked) {
        next.add(value)
      } else {
        next.delete(value)
      }
      return { ...prev, focus_sections: [...next] }
    })
  }

  const submit = async ({ applyFollowup }) => {
    setLoading(true)
    setError('')

    try {
      const form = new FormData()
      form.append('jd_text', jdText)
      if (resumeText.trim()) {
        form.append('resume_text', resumeText)
      }
      if (resumeFile) {
        form.append('resume_file', resumeFile)
      }
      if (parseurDocumentId.trim()) {
        form.append('parseur_document_id', parseurDocumentId.trim())
      }

      const activeSupplement = applyFollowup ? supplement : defaultSupplement
      if (
        activeSupplement.candidate_context ||
        activeSupplement.job_constraints ||
        activeSupplement.optimization_goal ||
        activeSupplement.focus_sections.length
      ) {
        form.append('supplement_json', JSON.stringify(activeSupplement))
      }

      if (result) {
        form.append('previous_result_json', JSON.stringify(result))
      }

      const resp = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        body: form,
      })

      if (!resp.ok) {
        const data = await resp.json()
        throw new Error(data.detail || '分析失败')
      }

      const data = await resp.json()
      if (result) {
        setHistory((prev) => [...prev, result])
      }
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="layout">
      <aside className="left-panel">
        <h1>Profile Polisher</h1>
        <p className="subtitle">上传简历 + JD，支持补充追问并对比结果变化</p>

        <label>简历上传（PDF / DOCX）</label>
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setResumeFile(e.target.files?.[0] ?? null)}
        />

        <label>或直接粘贴简历文本</label>
        <textarea value={resumeText} onChange={(e) => setResumeText(e.target.value)} rows={6} />

        <label>JD 文本</label>
        <textarea value={jdText} onChange={(e) => setJdText(e.target.value)} rows={8} />

        <label>Parseur Document ID（可选）</label>
        <input value={parseurDocumentId} onChange={(e) => setParseurDocumentId(e.target.value)} />

        <div className="actions">
          <button disabled={loading || !jdText.trim()} onClick={() => submit({ applyFollowup: false })}>
            {loading ? '分析中...' : '开始分析'}
          </button>
        </div>

        <section className="followup">
          <h2>追问补充（结构化）</h2>
          <label>候选人补充背景</label>
          <textarea
            value={supplement.candidate_context}
            onChange={(e) => setSupplement((prev) => ({ ...prev, candidate_context: e.target.value }))}
            rows={3}
          />

          <label>岗位补充约束</label>
          <textarea
            value={supplement.job_constraints}
            onChange={(e) => setSupplement((prev) => ({ ...prev, job_constraints: e.target.value }))}
            rows={3}
          />

          <label>本轮优化目标</label>
          <input
            value={supplement.optimization_goal}
            onChange={(e) => setSupplement((prev) => ({ ...prev, optimization_goal: e.target.value }))}
          />

          <div className="checkbox-grid">
            <label>
              <input
                type="checkbox"
                checked={supplement.focus_sections.includes('projects')}
                onChange={(e) => setFocusSection('projects', e.target.checked)}
              />
              聚焦项目
            </label>
            <label>
              <input
                type="checkbox"
                checked={supplement.focus_sections.includes('interview_questions')}
                onChange={(e) => setFocusSection('interview_questions', e.target.checked)}
              />
              聚焦面试题
            </label>
          </div>

          <button disabled={loading || !result} onClick={() => submit({ applyFollowup: true })}>
            应用补充并重新分析
          </button>
        </section>
      </aside>

      <main className="right-panel">
        <h2>分析结果</h2>
        {error && <div className="error">{error}</div>}
        {!result && <div className="placeholder">请先在左侧提交分析。</div>}

        {result && (
          <>
            <section className="card">
              <h3>匹配度</h3>
              <p>总分：{result.match.overall_score}</p>
              <ul>
                <li>Skills：{result.match.dimensions.skills}</li>
                <li>Projects：{result.match.dimensions.projects}</li>
                <li>Seniority：{result.match.dimensions.seniority}</li>
                <li>Domain：{result.match.dimensions.domain}</li>
              </ul>
            </section>

            <section className="card">
              <h3>结果对比</h3>
              {result.comparison.has_previous ? (
                <>
                  <ul>
                    {comparisonTips.map((tip) => (
                      <li key={tip}>{tip}</li>
                    ))}
                  </ul>
                  <p>新增优势：{result.comparison.added_strengths.join('；') || '无'}</p>
                  <p>移除差距：{result.comparison.removed_gaps.join('；') || '无'}</p>
                </>
              ) : (
                <p>当前是第一版结果，暂无历史对比。</p>
              )}
              <p>历史版本数：{history.length}</p>
            </section>

            <section className="card">
              <h3>差距分析</h3>
              <ul>
                {result.match.gaps.map((gap) => (
                  <li key={gap}>{gap}</li>
                ))}
              </ul>
            </section>

            <section className="card">
              <h3>项目优化建议</h3>
              {result.optimizations.map((item, idx) => (
                <div key={idx} className="suggestion">
                  <p><strong>项目：</strong>{item.project}</p>
                  <p><strong>改前：</strong>{item.before}</p>
                  <p><strong>改后：</strong>{item.after}</p>
                  <p><strong>原因：</strong>{item.reason}</p>
                </div>
              ))}
            </section>

            <section className="card">
              <h3>面试问题</h3>
              <ul>
                {result.interview_questions.map((q, idx) => (
                  <li key={`${q.category}-${idx}`}>
                    [{q.category}] {q.question}（考察：{q.focus}）
                  </li>
                ))}
              </ul>
            </section>
          </>
        )}
      </main>
    </div>
  )
}

export default App
