import { useState, useEffect } from 'react'
import data from './master_data.json'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkBreaks from 'remark-breaks'
import AdaptiveTutor from './AdaptiveTutor'
import './index.css'

function App() {
  const [theme, setTheme] = useState('light')
  const [selectedBlock, setSelectedBlock] = useState('Todos')
  const [selectedYear, setSelectedYear] = useState('Todos')
  const [searchTerm, setSearchTerm] = useState('')
  const [revealed, setRevealed] = useState({})
  const [isTutorMode, setIsTutorMode] = useState(false)

  // Extraer opciones únicas
  const blocks = ['Todos', ...new Set(data.map(q => q.block))]
  const years = ['Todos', ...new Set(data.map(q => q.year).filter(y => y))]

  // Filtrado
  const filteredData = data.filter(q => {
    if (selectedBlock !== 'Todos' && q.block !== selectedBlock) return false
    if (selectedYear !== 'Todos' && q.year !== selectedYear) return false
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      const textMatch = q.question && q.question.toLowerCase().includes(term)
      const criteriaMatch = q.criteria && q.criteria.toLowerCase().includes(term)
      if (!textMatch && !criteriaMatch) return false
    }
    return true
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light')

  const toggleReveal = (index) => {
    setRevealed(prev => ({ ...prev, [index]: !prev[index] }))
  }

  if (isTutorMode) {
    // Pasar solo las preguntas que tienen el parámetro 'b' necesario para el motor bayesiano
    const tutorQuestions = filteredData.filter(q => q.b !== undefined && q.b !== null)
    return <AdaptiveTutor questions={tutorQuestions} onExit={() => setIsTutorMode(false)} />
  }

  return (
    <div className="app-container">
      <header>
        <div>
          <h1>🧬 PAU Biología interactivo</h1>
          <p style={{color: 'var(--text-muted)'}}>Banco de preguntas 2011-2026</p>
        </div>
        <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
          <button className="primary-btn" onClick={() => setIsTutorMode(true)}>
            🧠 Entrenador Adaptativo
          </button>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? '🌙 Modo Oscuro' : '☀️ Modo Claro'}
          </button>
        </div>
      </header>

      <div className="filters">
        <select value={selectedBlock} onChange={e => setSelectedBlock(e.target.value)}>
          {blocks.map(b => <option key={b} value={b}>{b === 'Todos' ? 'Todos los bloques' : `Bloque ${b}`}</option>)}
        </select>
        
        <select value={selectedYear} onChange={e => setSelectedYear(e.target.value)}>
          {years.map(y => <option key={y} value={y}>{y === 'Todos' ? 'Todos los años' : y}</option>)}
        </select>
        
        <input 
          type="text" 
          placeholder="Buscar tema (ej. proteínas...)" 
          value={searchTerm} 
          onChange={e => setSearchTerm(e.target.value)} 
          style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border)', flex: '1', minWidth: '200px' }}
        />
      </div>

      <div className="questions-grid">
        {filteredData.map((q, i) => (
          <div key={i} className="question-card">
            <div className="card-header">
              <span className="badge">Bloque {q.block.split('-')[0]}</span>
              <span>{q.year} {q.month} - {q.option ? `Opc. ${q.option}` : ''}</span>
            </div>
            
            <div className="card-body">
              {q.image && (
                <div className="image-container" style={{ textAlign: 'center', margin: '1rem 0' }}>
                  <img src={q.image.startsWith('/') ? `.${q.image}` : q.image} alt="Imagen adjunta a la pregunta" style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: '8px', border: '1px solid var(--border)' }} />
                </div>
              )}
              <div className="question-text">
                <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>{q.question || "*(Pregunta no disponible en el texto original)*"}</ReactMarkdown>
              </div>
            </div>

            <button className="reveal-btn" onClick={() => toggleReveal(i)}>
              {revealed[i] ? 'Ocultar Criterios' : 'Ver Respuesta'}
            </button>

            {revealed[i] && (
              <div className="criteria-box">
                <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>{q.criteria || 'No hay criterios disponibles para esta pregunta.'}</ReactMarkdown>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
