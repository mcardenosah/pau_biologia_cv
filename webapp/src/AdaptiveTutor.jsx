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

  useEffect(() => {
    // Escoger la primera pregunta al montar si no hay ninguna y no hemos terminado
    if (!currentQuestion && availableQuestions.length > 0 && !isFinished) {
      const bestQ = selectBestQuestion(hypotheses, availableQuestions);
      setCurrentQuestion(bestQ);
    }
  }, [currentQuestion, availableQuestions, hypotheses, isFinished]);

  const handleScore = (score) => {
    // Actualizar Bayes
    const newHypotheses = updateHypotheses(hypotheses, currentQuestion, score);
    setHypotheses(newHypotheses);
    
    // Registrar historial
    const newHistory = [...history, { question: currentQuestion, score }];
    setHistory(newHistory);

    // Quitar pregunta de disponibles
    const remaining = availableQuestions.filter(q => q.id !== currentQuestion.id);
    setAvailableQuestions(remaining);

    // Condición de parada (mínimo 5 preguntas, y certeza >= 0.80)
    const maxProb = Math.max(...newHypotheses.map(h => h.prob));
    if ((maxProb >= 0.80 && newHistory.length >= 5) || remaining.length === 0) {
      setIsFinished(true);
      setCurrentQuestion(null);
    } else {
      // Siguiente pregunta
      const nextQ = selectBestQuestion(newHypotheses, remaining);
      setCurrentQuestion(nextQ);
      setShowCriteria(false);
    }
  };

  const getDominantLevel = () => {
    let dominant = hypotheses[0];
    for (const h of hypotheses) {
      if (h.prob > dominant.prob) dominant = h;
    }
    return dominant.level;
  };

  const getRecommendation = (level) => {
    if (level === 'Bajo') return "Te recomendamos repasar los conceptos fundamentales de los temas que más te han costado.";
    if (level === 'Medio') return "Tienes una buena base. Te sugiero reforzar practicando con criterios de corrección en mano.";
    return "¡Excelente dominio! Estás listo para afrontar cualquier pregunta de Selectividad sobre estos bloques.";
  };

  if (isFinished) {
    return (
      <div className="tutor-container">
        <h2>Sesión Finalizada</h2>
        <div className="diagnosis-box">
          <h3>Siguiente paso recomendado:</h3>
          <p style={{fontSize: '1.2rem', fontWeight: 'bold'}}>{getRecommendation(getDominantLevel())}</p>
        </div>
        
        <div className="stats-box">
          <h4>Probabilidades Finales:</h4>
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
        
        <button className="primary-btn" onClick={onExit} style={{marginTop: '2rem'}}>Volver al Banco</button>
      </div>
    );
  }

  return (
    <div className="tutor-container">
      <div className="tutor-header">
        <button onClick={onExit} className="back-btn">← Volver</button>
        <h2>Tutor Adaptativo Bayesiano</h2>
      </div>

      <div className="dashboard">
        <div className="entropia-info">
          Pregunta seleccionada para máxima ganancia de información
        </div>
        <div className="prob-bars">
          {hypotheses.map(h => (
            <div key={h.level} className="prob-bar-container">
              <span>{h.level}</span>
              <div className="prob-bar-bg">
                <div className="prob-bar-fill" style={{ width: `${(h.prob * 100).toFixed(1)}%` }}></div>
              </div>
            </div>
          ))}
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
              He pensado mi respuesta. Ver Criterios
            </button>
          ) : (
            <div className="criteria-box">
              <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                {currentQuestion.criteria || 'No hay criterios detallados.'}
              </ReactMarkdown>
              
              <div className="evaluation-box">
                <h4>Autoevaluación:</h4>
                <p>¿Qué tal lo has hecho comparado con los criterios oficiales?</p>
                <div className="eval-buttons">
                  <button className="eval-btn danger" onClick={() => handleScore(0)}>Mal (0)</button>
                  <button className="eval-btn warning" onClick={() => handleScore(0.5)}>Regular (0.5)</button>
                  <button className="eval-btn success" onClick={() => handleScore(1)}>Bien (1)</button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
