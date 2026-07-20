/**
 * Motor de Inferencia Bayesiana y Teoría de Respuesta al Ítem (IRT)
 * Basado en la metodología de Juan José de Haro.
 */

// Hipótesis iniciales sobre el nivel del estudiante (Prior distribution)
export const initialHypotheses = [
  { level: 'Bajo', theta: -2.0, prob: 1 / 3 },
  { level: 'Medio', theta: 0.0, prob: 1 / 3 },
  { level: 'Alto', theta: 2.0, prob: 1 / 3 },
];

/**
 * Modelo IRT (3PL) ajustado según la especificación operativa v2.6.
 * Calcula la probabilidad de que un estudiante con nivel theta responda bien a la pregunta.
 */
export function probCorrect(theta, q_a, q_b) {
  // Azar para preguntas abiertas
  const c = 0;
  // Discriminación efectiva objetivo
  const a_ef = 1.25;
  const a = a_ef / (1 - c);
  
  // Recortar dificultad (b) a la mitad central de la escala ([-1, 1] para n=3)
  const b = Math.max(-1, Math.min(1, q_b));

  const exponent = -a * (theta - b);
  const p = c + (1 - c) / (1 + Math.exp(exponent));
  
  // Techo de dominio
  return Math.min(0.95, p);
}

/**
 * Calcula la verosimilitud de una respuesta (score) dado un nivel theta.
 * score: 1 (bien), 0.5 (regular), 0 (mal)
 * Usa log-verosimilitud o probabilidad fraccional. P^S * (1-P)^(1-S)
 */
export function likelihood(theta, a, b, score) {
  const p = probCorrect(theta, a, b);
  // Prevenir log de 0
  const pSafe = Math.max(1e-5, Math.min(1 - 1e-5, p));
  return Math.pow(pSafe, score) * Math.pow(1 - pSafe, 1 - score);
}

/**
 * Entropía de Shannon de una distribución de probabilidades
 */
export function calculateEntropy(hypotheses) {
  return hypotheses.reduce((sum, h) => {
    if (h.prob <= 0) return sum;
    return sum - h.prob * Math.log2(h.prob);
  }, 0);
}

/**
 * Calcula la ganancia de información esperada para una pregunta.
 * Consideramos solo éxito (1) y fracaso (0) para la estimación de ganancia.
 */
export function expectedInformationGain(hypotheses, a, b) {
  const currentEntropy = calculateEntropy(hypotheses);

  // Probabilidad marginal de acertar (S=1) o fallar (S=0)
  let pMarginalS1 = 0;
  hypotheses.forEach(h => {
    pMarginalS1 += h.prob * probCorrect(h.theta, a, b);
  });
  const pMarginalS0 = 1 - pMarginalS1;

  // Posterior si S=1
  const postS1 = hypotheses.map(h => ({
    ...h,
    prob: (h.prob * probCorrect(h.theta, a, b)) / pMarginalS1
  }));
  
  // Posterior si S=0
  const postS0 = hypotheses.map(h => ({
    ...h,
    prob: (h.prob * (1 - probCorrect(h.theta, a, b))) / pMarginalS0
  }));

  const entropyS1 = calculateEntropy(postS1);
  const entropyS0 = calculateEntropy(postS0);

  const expectedEntropy = pMarginalS1 * entropyS1 + pMarginalS0 * entropyS0;
  return currentEntropy - expectedEntropy;
}

/**
 * Selecciona la mejor pregunta de un conjunto (la que maximiza la ganancia de información)
 */
export function selectBestQuestion(hypotheses, availableQuestions) {
  if (availableQuestions.length === 0) return null;

  let bestGain = -Infinity;
  let bestQuestion = availableQuestions[0];

  for (const q of availableQuestions) {
    const gain = expectedInformationGain(hypotheses, q.a, q.b);
    // Introducimos un pequeñísimo factor aleatorio para desempatar preguntas con parámetros idénticos
    const adjustedGain = gain + (Math.random() * 1e-6); 
    
    if (adjustedGain > bestGain) {
      bestGain = adjustedGain;
      bestQuestion = q;
    }
  }

  return bestQuestion;
}

/**
 * Actualiza las probabilidades de las hipótesis tras una respuesta usando el Teorema de Bayes
 */
export function updateHypotheses(hypotheses, question, score) {
  let evidence = 0;
  
  // Paso 1: Multiplicar Prior por Likelihood
  const unnormalized = hypotheses.map(h => {
    const lh = likelihood(h.theta, question.a, question.b, score);
    const prob = h.prob * lh;
    evidence += prob;
    return { ...h, prob };
  });

  // Paso 2: Normalizar (dividir por Evidencia)
  return unnormalized.map(h => ({
    ...h,
    prob: evidence > 0 ? h.prob / evidence : 1 / hypotheses.length
  }));
}
