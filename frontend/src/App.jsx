import { useState, useEffect } from 'react'

const API = '/api'

// ─── Styles ────────────────────────────────────────────────────────────────
const S = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    borderBottom: '1px solid var(--border)',
    padding: '0 2rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: '56px',
    background: 'var(--paper)',
    position: 'sticky',
    top: 0,
    zIndex: 10,
  },
  logo: {
    fontFamily: 'var(--font-display)',
    fontSize: '1.25rem',
    color: 'var(--ink)',
    letterSpacing: '-0.01em',
  },
  badge: {
    fontFamily: 'var(--font-mono)',
    fontSize: '0.7rem',
    background: 'var(--amber-light)',
    color: 'var(--amber-dark)',
    padding: '2px 8px',
    borderRadius: '20px',
    letterSpacing: '0.04em',
  },
  main: {
    flex: 1,
    maxWidth: '820px',
    width: '100%',
    margin: '0 auto',
    padding: '3rem 2rem 4rem',
  },
  hero: {
    marginBottom: '3rem',
  },
  heroTitle: {
    fontFamily: 'var(--font-display)',
    fontSize: '2.6rem',
    lineHeight: 1.15,
    color: 'var(--ink)',
    marginBottom: '0.75rem',
    letterSpacing: '-0.02em',
  },
  heroSub: {
    color: 'var(--ink-3)',
    fontSize: '1rem',
    maxWidth: '480px',
  },
  card: {
    background: 'var(--paper)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '1.5rem',
    marginBottom: '1.25rem',
  },
  label: {
    display: 'block',
    fontFamily: 'var(--font-mono)',
    fontSize: '0.7rem',
    letterSpacing: '0.08em',
    color: 'var(--ink-3)',
    textTransform: 'uppercase',
    marginBottom: '0.5rem',
  },
  textarea: {
    width: '100%',
    minHeight: '160px',
    padding: '0.75rem',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    background: 'var(--paper-2)',
    color: 'var(--ink)',
    fontFamily: 'var(--font-mono)',
    fontSize: '0.82rem',
    lineHeight: 1.6,
    resize: 'vertical',
    outline: 'none',
    transition: 'border-color var(--transition)',
  },
  select: {
    width: '100%',
    padding: '0.65rem 0.75rem',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    background: 'var(--paper-2)',
    color: 'var(--ink)',
    fontFamily: 'var(--font-body)',
    fontSize: '0.95rem',
    outline: 'none',
    cursor: 'pointer',
  },
  row: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '1rem',
    marginBottom: '1.25rem',
  },
  btn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.7rem 1.6rem',
    background: 'var(--ink)',
    color: 'var(--paper)',
    border: 'none',
    borderRadius: 'var(--radius)',
    fontFamily: 'var(--font-body)',
    fontSize: '0.95rem',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background var(--transition)',
  },
  btnSecondary: {
    background: 'transparent',
    color: 'var(--ink-2)',
    border: '1px solid var(--border)',
    padding: '0.5rem 1rem',
    borderRadius: 'var(--radius)',
    fontFamily: 'var(--font-body)',
    fontSize: '0.85rem',
    cursor: 'pointer',
  },
  section: {
    marginTop: '2.5rem',
  },
  sectionTitle: {
    fontFamily: 'var(--font-display)',
    fontSize: '1.5rem',
    marginBottom: '1rem',
    color: 'var(--ink)',
    display: 'flex',
    alignItems: 'center',
    gap: '0.6rem',
  },
  pill: (type) => {
    const map = {
      missing: { bg: 'var(--red-light)', color: 'var(--red)' },
      transferable: { bg: 'var(--green-light)', color: 'var(--green)' },
      ai: { bg: 'var(--amber-light)', color: 'var(--amber-dark)' },
      fallback: { bg: 'var(--paper-3)', color: 'var(--ink-3)' },
    }
    const { bg, color } = map[type] || map.fallback
    return {
      display: 'inline-block',
      padding: '3px 10px',
      borderRadius: '20px',
      background: bg,
      color,
      fontFamily: 'var(--font-mono)',
      fontSize: '0.78rem',
      fontWeight: 500,
    }
  },
  skillGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.5rem',
    marginTop: '0.5rem',
  },
  roadmapItem: {
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '1.25rem',
    marginBottom: '0.75rem',
    background: 'var(--paper)',
    position: 'relative',
  },
  stepNum: {
    fontFamily: 'var(--font-mono)',
    fontSize: '0.7rem',
    color: 'var(--ink-3)',
    letterSpacing: '0.06em',
    marginBottom: '0.3rem',
  },
  roadmapSkill: {
    fontFamily: 'var(--font-display)',
    fontSize: '1.2rem',
    color: 'var(--ink)',
    marginBottom: '0.3rem',
  },
  roadmapWhy: {
    fontSize: '0.9rem',
    color: 'var(--ink-2)',
    marginBottom: '0.75rem',
    lineHeight: 1.5,
  },
  resourceRow: {
    display: 'flex',
    gap: '0.75rem',
    flexWrap: 'wrap',
  },
  resourceTag: (paid) => ({
    fontFamily: 'var(--font-mono)',
    fontSize: '0.75rem',
    padding: '3px 10px',
    borderRadius: '4px',
    background: paid ? 'var(--paper-2)' : 'var(--paper-2)',
    color: paid ? 'var(--ink-2)' : 'var(--ink-2)',
    border: '1px solid var(--border)',
  }),
  weeks: {
    fontFamily: 'var(--font-mono)',
    fontSize: '0.72rem',
    color: 'var(--ink-3)',
    marginLeft: 'auto',
    alignSelf: 'center',
    whiteSpace: 'nowrap',
  },
  summary: {
    background: 'var(--paper-2)',
    border: '1px solid var(--border)',
    borderLeft: '3px solid var(--amber)',
    borderRadius: 'var(--radius)',
    padding: '1rem 1.25rem',
    fontSize: '0.95rem',
    color: 'var(--ink-2)',
    lineHeight: 1.7,
    marginBottom: '1.5rem',
  },
  error: {
    background: 'var(--red-light)',
    border: '1px solid #f5c0c0',
    borderRadius: 'var(--radius)',
    padding: '0.75rem 1rem',
    color: 'var(--red)',
    fontSize: '0.9rem',
    marginBottom: '1rem',
  },
  spinner: {
    display: 'inline-block',
    width: '14px',
    height: '14px',
    border: '2px solid rgba(255,255,255,0.3)',
    borderTopColor: '#fff',
    borderRadius: '50%',
    animation: 'spin 0.7s linear infinite',
  },
}

// ─── Component: SkillPill ──────────────────────────────────────────────────
function SkillPill({ skill, type }) {
  return <span style={S.pill(type)}>{skill}</span>
}

// ─── Component: RoadmapCard ────────────────────────────────────────────────
function RoadmapCard({ item, index }) {
  return (
    <div style={S.roadmapItem}>
      <div style={S.stepNum}>STEP {index + 1} · {item.estimated_weeks} {item.estimated_weeks === 1 ? 'week' : 'weeks'}</div>
      <div style={S.roadmapSkill}>{item.skill}</div>
      <div style={S.roadmapWhy}>{item.why}</div>
      <div style={{ ...S.resourceRow, alignItems: 'center', marginBottom: item.certifications?.length ? '0.5rem' : 0 }}>
        <span style={S.resourceTag(false)}><strong>Primary resource:</strong> {item.free_resource}</span>
        <span style={S.resourceTag(true)}><strong>Alternative:</strong> {item.paid_resource}</span>
      </div>
      {item.certifications?.length > 0 && (
        <div
          style={{
            fontSize: '0.9rem',
            color: 'var(--amber-dark)',
            fontWeight: 500,
            marginTop: '0.15rem',
          }}
        >
          <strong>Recommended certs:</strong> {item.certifications.join(', ')}
        </div>
      )}
    </div>
  )
}

// ─── Component: Results ────────────────────────────────────────────────────
function Results({ data }) {
  const totalWeeks = data.roadmap.reduce((a, b) => a + b.estimated_weeks, 0)
  const hasJobs = data.suggested_jobs && data.suggested_jobs.length > 0

  return (
    <div style={{ animation: 'fadeIn 0.4s ease' }}>
      {/* Header bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', color: 'var(--ink-3)' }}>
          Analysis for
        </span>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', color: 'var(--ink)' }}>
          {data.target_role}
        </span>
        <span style={S.pill(data.ai_powered ? 'ai' : 'fallback')}>
          {data.ai_powered ? '✦ AI analysis' : '⚙ rule-based fallback'}
        </span>
      </div>

      {/* Summary */}
      <div style={S.summary}>{data.summary}</div>

      {/* Skills grid */}
      <div style={S.row}>
        <div style={S.card}>
          <span style={S.label}>Missing skills · {data.missing_skills.length}</span>
          <div style={S.skillGrid}>
            {data.missing_skills.length === 0
              ? <span style={{ color: 'var(--green)', fontSize: '0.9rem' }}>✓ No gaps found!</span>
              : data.missing_skills.map(s => <SkillPill key={s} skill={s} type="missing" />)
            }
          </div>
        </div>
        <div style={S.card}>
          <span style={S.label}>Transferable skills · {data.transferable_skills.length}</span>
          <div style={S.skillGrid}>
            {data.transferable_skills.length === 0
              ? <span style={{ color: 'var(--ink-3)', fontSize: '0.9rem' }}>None detected</span>
              : data.transferable_skills.map(s => <SkillPill key={s} skill={s} type="transferable" />)
            }
          </div>
        </div>
      </div>

      {/* Relevant job postings */}
      {hasJobs && (
        <div style={S.section}>
          <div style={S.sectionTitle}>
            <span>Relevant job postings</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--ink-3)' }}>
              Live roles for "{data.target_role}"
            </span>
          </div>
          <div style={S.card}>
            {data.suggested_jobs.map((job, i) => (
              <div key={i} style={{ marginBottom: '0.9rem' }}>
                <div style={{ fontWeight: 600 }}>
                  {job.title}
                  {job.company && ` · ${job.company}`}
                </div>
                {job.location && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--ink-3)' }}>{job.location}</div>
                )}
                {job.snippet && (
                  <div style={{ fontSize: '0.85rem', color: 'var(--ink-2)', marginTop: '0.25rem' }}>
                    {job.snippet}
                  </div>
                )}
                {job.link && (
                  <a
                    href={job.link}
                    target="_blank"
                    rel="noreferrer"
                    style={{ fontSize: '0.8rem', color: 'var(--amber-dark)' }}
                  >
                    View posting
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Roadmap */}
      {data.roadmap.length > 0 && (
        <div style={S.section}>
          <div style={S.sectionTitle}>
            <span>Learning roadmap</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--ink-3)', fontWeight: 400 }}>
              {totalWeeks} weeks total
            </span>
          </div>
          {data.roadmap.map((item, i) => (
            <RoadmapCard key={item.skill} item={item} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Main App ──────────────────────────────────────────────────────────────
export default function App() {
  const [name, setName] = useState('')
  const [education, setEducation] = useState('')
  const [experiences, setExperiences] = useState([
    { role: '', company: '', duration: '', bulletsText: '' },
  ])
  const [skillsInput, setSkillsInput] = useState('')
  const [projectsInput, setProjectsInput] = useState('')
  const [certsInput, setCertsInput] = useState('')

  const [targetRole, setTargetRole] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('')
  const [roles, setRoles] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API}/roles`).then(r => r.json()).then(setRoles).catch(() => {})
  }, [])

  const handleExperienceChange = (index, field, value) => {
    setExperiences(prev => {
      const next = [...prev]
      next[index] = { ...next[index], [field]: value }
      return next
    })
  }

  const addExperience = () => {
    setExperiences(prev => [...prev, { role: '', company: '', duration: '', bulletsText: '' }])
  }

  const removeExperience = (index) => {
    setExperiences(prev => prev.length <= 1 ? prev : prev.filter((_, i) => i !== index))
  }

  const buildResumeTextFromForm = () => {
    const skills = skillsInput.split(',').map(s => s.trim()).filter(Boolean)
    const projects = projectsInput.split(',').map(s => s.trim()).filter(Boolean)
    const certs = certsInput.split(',').map(s => s.trim()).filter(Boolean)

    const experienceLines = experiences
      .map(exp => {
        const bullets = exp.bulletsText
          .split(/\n|;/)
          .map(b => b.trim())
          .filter(Boolean)
        if (!exp.role && !exp.company && !exp.duration && bullets.length === 0) {
          return null
        }
        const header = `${exp.role || 'Role'} at ${exp.company || 'Company'} (${exp.duration || ''})`
        const body = bullets.length ? `: ${bullets.join('; ')}` : ''
        return `${header}${body}`
      })
      .filter(Boolean)

    return [
      name && `Name: ${name}`,
      education && `Education: ${education}`,
      skills.length && `Skills: ${skills.join(', ')}`,
      experienceLines.length && `Experience: \n- ${experienceLines.join('\n- ')}`,
      projects.length && `Projects: ${projects.join(', ')}`,
      certs.length && `Certifications: ${certs.join(', ')}`,
    ]
      .filter(Boolean)
      .join('\n')
  }

  const handleAnalyze = async () => {
    const resumeText = buildResumeTextFromForm()

    if (!resumeText.trim() || !targetRole.trim()) {
      setError('Please fill in your resume details and select a target role.')
      return
    }
    setError(null)
    setLoading(true)
    setResult(null)
    try {
      const payload = {
        resume_text: resumeText,
        target_role: targetRole,
        experience_level: experienceLevel || null,
      }
      const res = await fetch(`${API}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Analysis failed.')
      }
      setResult(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={S.page}>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
        textarea:focus, select:focus { border-color: var(--amber) !important; }
        button:hover { opacity: 0.88; }
      `}</style>

      <header style={S.header}>
        <div style={S.logo}>SkillBridge</div>
        <span style={S.badge}>CAREER NAVIGATOR</span>
      </header>

      <main style={S.main}>
        <div style={S.hero}>
          <h1 style={S.heroTitle}>Find your<br /><em>skill gaps.</em></h1>
          <p style={S.heroSub}>
            Enter your background, pick a target role, and get a personalised learning roadmap powered by AI.
          </p>
        </div>

        {/* Structured Resume Form */}
        <div style={S.card}>
          <label style={S.label}>Basic info</label>
          <input
            style={{ ...S.select, marginBottom: '0.5rem' }}
            type="text"
            placeholder="Your name (optional)"
            value={name}
            onChange={e => setName(e.target.value)}
          />
          <input
            style={S.select}
            type="text"
            placeholder="Education (e.g. BS Computer Science, State University, 2024)"
            value={education}
            onChange={e => setEducation(e.target.value)}
          />
        </div>

        <div style={S.card}>
          <label style={S.label}>Experience</label>
          {experiences.map((exp, index) => (
            <div key={index} style={{ marginBottom: '1rem', borderBottom: index < experiences.length - 1 ? '1px dashed var(--border)' : 'none', paddingBottom: index < experiences.length - 1 ? '0.75rem' : 0 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.2fr 0.8fr', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <input
                  style={S.select}
                  type="text"
                  placeholder="Role (e.g. Software Engineer)"
                  value={exp.role}
                  onChange={e => handleExperienceChange(index, 'role', e.target.value)}
                />
                <input
                  style={S.select}
                  type="text"
                  placeholder="Company"
                  value={exp.company}
                  onChange={e => handleExperienceChange(index, 'company', e.target.value)}
                />
                <input
                  style={S.select}
                  type="text"
                  placeholder="Duration (e.g. 2 years)"
                  value={exp.duration}
                  onChange={e => handleExperienceChange(index, 'duration', e.target.value)}
                />
              </div>
              <textarea
                style={S.textarea}
                placeholder="Key bullet points (one per line or separated by ;)"
                value={exp.bulletsText}
                onChange={e => handleExperienceChange(index, 'bulletsText', e.target.value)}
              />
              {experiences.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeExperience(index)}
                  style={{ ...S.btnSecondary, marginTop: '0.4rem' }}
                >
                  Remove this experience
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addExperience}
            style={{ ...S.btnSecondary, marginTop: '0.25rem' }}
          >
            + Add another experience
          </button>
        </div>

        <div style={S.card}>
          <label style={S.label}>Skills</label>
          <input
            style={S.select}
            type="text"
            placeholder="Comma-separated skills (e.g. Python, SQL, Docker)"
            value={skillsInput}
            onChange={e => setSkillsInput(e.target.value)}
          />
        </div>

        <div style={S.card}>
          <label style={S.label}>Projects</label>
          <input
            style={S.select}
            type="text"
            placeholder="Comma-separated project names (optional)"
            value={projectsInput}
            onChange={e => setProjectsInput(e.target.value)}
          />
        </div>

        <div style={S.card}>
          <label style={S.label}>Certifications</label>
          <input
            style={S.select}
            type="text"
            placeholder="Comma-separated certifications (optional)"
            value={certsInput}
            onChange={e => setCertsInput(e.target.value)}
          />
        </div>

        {/* Role Selector */}
        <div style={S.card}>
          <label style={S.label}>Target role</label>
          <select
            style={S.select}
            value={targetRole}
            onChange={e => setTargetRole(e.target.value)}
          >
            <option value="">Select a job title...</option>
            {roles.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>

        {/* Experience Level Selector */}
        <div style={S.card}>
          <label style={S.label}>Experience level</label>
          <select
            style={S.select}
            value={experienceLevel}
            onChange={e => setExperienceLevel(e.target.value)}
          >
            <option value="">Choose your level (optional)...</option>
            <option value="junior">Junior / Entry-level</option>
            <option value="mid">Mid-level</option>
            <option value="senior">Senior / Lead</option>
          </select>
        </div>

        {error && <div style={S.error}>{error}</div>}

        <button
          style={{ ...S.btn, opacity: loading ? 0.7 : 1 }}
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading
            ? <><span style={S.spinner} /> Analysing...</>
            : '→ Analyse my gaps'
          }
        </button>

        {result && (
          <div style={S.section}>
            <Results data={result} />
          </div>
        )}
      </main>
    </div>
  )
}
