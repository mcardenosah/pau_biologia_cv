import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { initialHypotheses, selectBestQuestion, updateHypotheses, calculateEntropy } from './bayesEngine';
import './tutor.css';

export default function AdaptiveTutor({ questions, onExit }) {
  const [hypotheses, setHypotheses] = useState(initialHypotheses);
  const [availableQuestions, setAvailableQuestions] = useState(questions);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [showCriteria, setShowCriteria] = useState(false);
  const [history, setHistory] = useState([]);
  const [isFinished, setIsFinished] = useState(false);
  
  // Checklists y feedback
  const [checkedItems, setCheckedItems] = useState(new Set());
  const [transitionMessage, setTransitionMessage] = useState("");

  useEffect(() => {
    if (!currentQuestion && availableQuestions.length > 0 && !isFinished) {
      const bestQ = selectBestQuestion(hypotheses, availableQuestions);
      setCurrentQuestion(bestQ);
    }
  }, [currentQuestion, availableQuestions, hypotheses, isFinished]);

  const parseCriteria = (text) => {
    if (!text) return [];
    
    // 1. Dividir por saltos de línea
    let rawLines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    
    // 2. Romper párrafos largos por punto y seguido para evitar checklist de un solo item gigante
    let items = [];
    for (let line of rawLines) {
      if (line.includes('. ') && line.length > 50) {
        // Dividir por punto seguido de espacio y letra mayúscula, o espacio y letra minúscula con paréntesis (ej: " b) ")
        const parts = line.split(/\.\s+(?=[A-ZÁÉÍÓÚÑ]|[a-z]\)\s)/);
        parts.forEach((p, idx) => {
          items.push(p.trim() + (idx < parts.length - 1 ? '.' : ''));
        });
      } else {
        items.push(line);
      }
    }
    
    // 3. Limpiar líneas informativas sin opción a check
    return items.filter(item => {
      const lower = item.toLowerCase();
      // Eliminar textos que son solo puntuaciones (ej: "0,5 puntos", "(1 punto)")
      if (/^\(?\d+[,.]?\d*\s*puntos?\)?\.?$/.test(lower)) return false;
      // Eliminar cabeceras redundantes
      if (lower === 'criterios de corrección:' || lower === 'criterios:' || lower === 'respuesta:' || lower.replace(':','').trim() === 'el alumno contestará' || lower.includes('el alumno contestará:')) return false;
      // Eliminar ítems vacíos o absurdamente cortos ("a)", "-")
      if (item.length < 5) return false;
      return true;
    });
  };

  const criteriaItems = parseCriteria(currentQuestion?.criteria);

  const handleScore = () => {
    // Calcular el score en función de la checklist parseada correctamente
    let score = 1;
    if (criteriaItems.length > 0) {
      score = checkedItems.size / criteriaItems.length;
    }

    // Asegurar que el score nunca sobrepase 1 (por si acaso)
    score = Math.min(1, Math.max(0, score));

    // Actualizar Bayes
    const newHypotheses = updateHypotheses(hypotheses, currentQuestion, score);
    setHypotheses(newHypotheses);
    
    // Registrar historial
    const newHistory = [...history, { question: currentQuestion, score }];
    setHistory(newHistory);

    // Quitar pregunta de disponibles
    const remaining = availableQuestions.filter(q => q.id !== currentQuestion.id);
    setAvailableQuestions(remaining);

    // Condición de parada
    const maxProb = Math.max(...newHypotheses.map(h => h.prob));
    if ((maxProb >= 0.80 && newHistory.length >= 5) || remaining.length === 0) {
      setIsFinished(true);
      setCurrentQuestion(null);
      setTransitionMessage("");
    } else {
      // Siguiente pregunta y micro-feedback
      if (score < 0.4) {
        setTransitionMessage(`Resultado registrado (${(score*100).toFixed(0)}%). Ajustando modelo para seleccionar un concepto de refuerzo...`);
      } else if (score < 0.8) {
        setTransitionMessage(`Resultado registrado (${(score*100).toFixed(0)}%). Calibrando siguiente pregunta...`);
      } else {
        setTransitionMessage(`Resultado registrado (${(score*100).toFixed(0)}%). Evaluando siguiente nivel de complejidad...`);
      }
      
      const nextQ = selectBestQuestion(newHypotheses, remaining);
      setCurrentQuestion(nextQ);
      setShowCriteria(false);
      setCheckedItems(new Set());
    }
  };

  const toggleCheck = (idx) => {
    const newSet = new Set(checkedItems);
    if (newSet.has(idx)) newSet.delete(idx);
    else newSet.add(idx);
    setCheckedItems(newSet);
  };

  const getDominantLevel = () => {
    let dominant = hypotheses[0];
    for (const h of hypotheses) {
      if (h.prob > dominant.prob) dominant = h;
    }
    return dominant.level;
  };

  const renderAnalyticFeedback = () => {
    // Agrupar historia por bloque
    const blockStats = {};
    for (const entry of history) {
      const block = entry.question.block;
      if (!blockStats[block]) blockStats[block] = { totalScore: 0, count: 0, mistakes: [] };
      blockStats[block].totalScore += entry.score;
      blockStats[block].count += 1;
      if (entry.score < 1) {
        blockStats[block].mistakes.push(entry);
      }
    }

    return (
      <div className="analytics-container" style={{textAlign: 'left', marginTop: '1rem'}}>
        <h3 style={{borderBottom: '2px solid var(--primary)', paddingBottom: '0.5rem'}}>Rendimiento Analítico por Bloques Temáticos</h3>
        {Object.entries(blockStats).map(([block, stats]) => {
          const avg = stats.totalScore / stats.count;
          let icon = '🔴';
          let color = '#d32f2f';
          if (avg >= 0.8) { icon = '🟢'; color = '#388e3c'; }
          else if (avg >= 0.5) { icon = '🟠'; color = '#f57c00'; }
          
          return (
            <div key={block} style={{margin: '1rem 0', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px', borderLeft: `5px solid ${color}`}}>
              <h4 style={{margin: '0 0 0.5rem 0', color: 'var(--text)'}}>{icon} {block} ({(avg*100).toFixed(0)}% éxito)</h4>
              {stats.mistakes.length === 0 ? (
                <p style={{margin: 0, color: 'var(--text-muted)'}}>Dominio consolidado en las preguntas evaluadas de este bloque.</p>
              ) : (
                <div>
                  <p style={{margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: 'bold'}}>Conceptos a reforzar (preguntas con fallos):</p>
                  <ul style={{margin: 0, paddingLeft: '1.5rem', fontSize: '0.9rem', color: 'var(--text-muted)'}}>
                    {stats.mistakes.map((m, i) => (
                      <li key={i}>{m.question.year} {m.question.month} {m.question.option && `Opc. ${m.question.option}`}: Puntaje obtenido {(m.score*100).toFixed(0)}%</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  if (isFinished) {
    return (
      <div className="tutor-container">
        <h2>Evaluación Diagnóstica Finalizada</h2>
        
        <div className="stats-box" style={{marginBottom: '2rem'}}>
          <h4>Estimación global del algoritmo: Nivel {getDominantLevel()}</h4>
          {hypotheses.map(h => (
            <div key={h.level} className="prob-bar-container">
              <span>{h.level}</span>
              <div className="prob-bar-bg">
                <div className="prob-bar-fill" style={{ width: `${(h.prob * 100).toFixed(1)}%` }}></div>
              </div>
              <span>{(h.prob * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        {renderAnalyticFeedback()}
        
        <button className="primary-btn" onClick={onExit} style={{marginTop: '2rem'}}>Volver al Banco</button>
      </div>
    );
  }



  return (
    <div className="tutor-container">
      <div className="tutor-header">
        <button onClick={onExit} className="back-btn">← Volver</button>
        <h2>Entrenador Adaptativo</h2>
      </div>

      <div className="dashboard">
        <div className="entropia-info">
          {transitionMessage || "Calibración inicial del modelo probabilístico en curso..."}
        </div>
      </div>

      {currentQuestion && (
        <div className="question-card tutor-card">
          <div className="card-header">
            <span className="badge">Bloque {currentQuestion.block.split('-')[0]}</span>
            <span>{currentQuestion.year} {currentQuestion.month}</span>
          </div>
          <div className="card-body">
            {currentQuestion.image && (
              <div className="image-container" style={{ textAlign: 'center', margin: '1rem 0' }}>
                <img src={currentQuestion.image.startsWith('/') ? `.${currentQuestion.image}` : currentQuestion.image} alt="Imagen didáctica" style={{ maxWidth: '100%', maxHeight: '350px', borderRadius: '8px', border: '1px solid var(--border)' }} />
              </div>
            )}
            <div className="question-text">
              <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                {currentQuestion.question}
              </ReactMarkdown>
            </div>
          </div>

          {!showCriteria ? (
            <button className="reveal-btn" onClick={() => setShowCriteria(true)}>
              Ver Criterios de Corrección
            </button>
          ) : (
            <div className="criteria-box">
              <h4>Criterios Oficiales:</h4>
              <p style={{fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem'}}>
                Marca estrictamente los elementos que has incluido en tu respuesta mental o escrita:
              </p>
              
              {criteriaItems.length > 0 ? (
                <div className="checklist-container" style={{display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.5rem'}}>
                  {criteriaItems.map((item, idx) => (
                    <label key={idx} style={{display: 'flex', alignItems: 'flex-start', gap: '0.5rem', cursor: 'pointer', padding: '0.5rem', backgroundColor: checkedItems.has(idx) ? '#e8f5e9' : 'transparent', borderRadius: '4px', transition: 'background 0.2s'}}>
                      <input 
                        type="checkbox" 
                        checked={checkedItems.has(idx)}
                        onChange={() => toggleCheck(idx)}
                        style={{marginTop: '0.3rem'}}
                      />
                      <div style={{flex: 1}}>
                        <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>{item}</ReactMarkdown>
                      </div>
                    </label>
                  ))}
                </div>
              ) : (
                <p>No hay criterios detallados disponibles.</p>
              )}
              
              <div className="evaluation-box" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <div>
                  <span style={{fontWeight: 'bold'}}>Puntuación autoevaluada: </span>
                  {criteriaItems.length > 0 ? ((checkedItems.size / criteriaItems.length)*100).toFixed(0) : 100}%
                </div>
                <button className="primary-btn" onClick={handleScore}>
                  Registrar Respuesta y Continuar
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
