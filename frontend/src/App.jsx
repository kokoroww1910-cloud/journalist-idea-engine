import { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

export default function App() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!topic.trim()) {
      setError('请输入新闻话题')
      return
    }

    setLoading(true)
    setError('')
    try {
      const resp = await fetch(`${API_BASE}/api/idea`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })

      if (!resp.ok) {
        throw new Error('分析失败，请稍后重试')
      }

      const data = await resp.json()
      setResult(data)
    } catch (err) {
      setError(err.message || '请求失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="top">
        <h1>Journalist Idea Engine V1</h1>
        <p>新闻选题引擎 · 帮助记者发现线索、趋势与调查方向</p>
      </header>

      <form className="panel" onSubmit={handleSubmit}>
        <label htmlFor="topic">输入新闻话题</label>
        <input
          id="topic"
          placeholder="例如：新能源汽车、平台经济监管、芯片供应链"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />
        <button type="submit" disabled={loading}>{loading ? '分析中...' : '开始分析'}</button>
      </form>

      {error && <section className="error">错误：{error}</section>}

      {result && (
        <main className="content">
          <section className="scores">
            <article className="card">
              <h2>Impact Score</h2>
              <strong>{result.impact_score}</strong>
            </article>
            <article className="card">
              <h2>Potential Score</h2>
              <strong>{result.potential_score}</strong>
            </article>
          </section>

          <section className="block">
            <h2>新闻 Signals</h2>
            <ul>
              {result.signals.map((item) => (
                <li key={item.url}>
                  <a href={item.url} target="_blank" rel="noreferrer">{item.title}</a>
                  <div>{item.source} · {item.published_date || '时间未知'}</div>
                </li>
              ))}
            </ul>
          </section>

          <section className="block">
            <h2>推荐选题方向</h2>
            <div className="angles">
              {result.angles.map((angle, idx) => (
                <article className="card" key={`${angle.title}-${idx}`}>
                  <h3>{angle.title}</h3>
                  <p>{angle.explanation}</p>
                  <small>为什么重要：{angle.why_it_matters}</small>
                </article>
              ))}
            </div>
          </section>

          <section className="block">
            <h2>关键词延伸</h2>
            <div className="tags">
              {result.keywords.map((k) => (
                <span key={k}>{k}</span>
              ))}
            </div>
          </section>
        </main>
      )}
    </div>
  )
}
