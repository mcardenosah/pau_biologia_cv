# Especificación operativa para IA

**Versión 2.6**

## Propósito

Este documento sirve para que una IA implemente recursos educativos adaptativos bayesianos de forma fiable.  
Es una especificación operativa breve.  
Si hace falta fundamento teórico, ejemplos o justificación matemática, consulta el protocolo (https://jjdeharo.github.io/recursos-adaptativos/documentacion.html) y los fundamentos matemáticos (https://jjdeharo.github.io/recursos-adaptativos/matematicas.html). Si solo tienes adjunto este archivo y no puedes navegar, actúa con lo que aquí se especifica; no inventes contenido de esos documentos.
Si hubiera conflicto entre ambos documentos, prevalece este.

## Instrucción de uso

Adjunta este documento a la IA y usa este prompt:

> Lee el documento adjunto e implementa el recurso siguiendo las reglas operativas aplicables al tipo de recurso solicitado.

## Flujo obligatorio

1. Antes de implementar, comprueba si tienes esta información:
   - tema;
   - curso o edad;
   - objetivo de aprendizaje;
   - tipo de recurso;
   - finalidad principal;
   - número de hipótesis o niveles;
   - tipo de interacción;
   - número aproximado de preguntas o pasos;
   - salida final esperada.
2. Si falta información esencial, pregunta solo por lo imprescindible.
3. Si la información ya está dada, no repitas preguntas y pasa a implementar.
4. El resultado debe ser un recurso web estático en `HTML + CSS + JavaScript`, preferentemente sin backend, salvo que se pida explícitamente otro formato. Puede organizarse en uno o varios archivos si eso mejora la claridad, el mantenimiento o la reutilización.

## Perfil y modo: qué secciones aplican

Con la información anterior, clasifica el recurso **antes de implementar**. Esta clasificación decide qué secciones de este documento debes aplicar; no mezcles reglas de perfiles o modos distintos.

**Perfil** (qué se estima; los criterios de decisión están en «Elección del modelo»):

- `A` · **Ordinal**: niveles ordenados de dominio, globales o por categoría.
- `B` · **Nominal excluyente**: hipótesis alternativas; solo una puede ser cierta en cada alumno.
- `C` · **Multifactorial**: errores o factores que pueden coexistir.
- `A+C` · **Combinado**: nivel ordinal y factores de error a la vez.

**Modo** (cómo termina la sesión):

- `Diagnóstico`: la sesión converge y se cierra con un resultado.
- `Práctica`: sin final previsto; estimación viva con olvido.
- `Itinerario`: etapas sucesivas con promoción entre ellas.

| Sección | Aplica solo si |
|---|---|
| Estado del alumno (escala `theta`) | perfil `A` o `A+C` (en `B` y `C` no existe `theta`) |
| Verosimilitudes · parte IRT 3PL | perfil `A` o la parte de nivel de `A+C` |
| Verosimilitudes · parte nominal y por perfiles | perfil `B`, `C` o `A+C` |
| Respuestas con crédito parcial | hay ítems con grados o por pasos |
| Suelo de azar en ítems compuestos | hay ítems de varios componentes |
| Diagnóstico multidimensional | perfil `C`, `A+C`, o varias distribuciones en paralelo |
| Selección adaptativa · bloques pedagógicos | perfil `A+C` o varias distribuciones en paralelo |
| Selección adaptativa · dos fases y utilidad `α` | modo `Práctica` |
| Criterio de parada | modo `Diagnóstico` o `Itinerario` |
| Refuerzo continuo sin parada | modo `Práctica` |
| Itinerarios por etapas | modo `Itinerario` |
| Validación y fiabilidad | finalidad diagnóstica o promoción de etapas |

Las secciones no listadas aplican siempre. Ejemplos de mezcla indebida que esta tabla evita: activar olvido (`lambda < 1`) en un diagnóstico de sesión corta; calcular una `theta` esperada en perfiles `B` o `C`; exigir ítems de salida fuera de un itinerario; montar bloques pedagógicos con una sola distribución.

## Reglas de diseño

- El recurso no debe ser lineal si la finalidad exige adaptación.
- Cada respuesta del alumno debe modificar el estado estimado del sistema.
- Interpreta cada respuesta como evidencia parcial sobre una o varias hipótesis, no como prueba directa de conocimiento.
- Ninguna respuesta aislada debe eliminar una hipótesis ni imponer un nivel máximo irreversible. Todas las hipótesis deben conservar probabilidad distinta de cero y el alumno debe poder cambiar el diagnóstico con evidencia posterior suficiente. En particular, fallar una pregunta fácil no debe impedir alcanzar el nivel más alto si después demuestra dominio de forma consistente.
- La adaptación puede afectar a:
  - la siguiente pregunta;
  - la dificultad;
  - el tipo de actividad;
  - la explicación;
  - la ayuda o las pistas;
  - el itinerario;
  - el momento de finalizar.
- El resultado final debe ser pedagógico, no solo una puntuación.

## Estado del alumno

- Representa el estado del alumno como una distribución de probabilidad sobre `n` hipótesis.
- Prior de hipótesis de **nivel**: si no hay información previa fiable, usa distribución uniforme. Prior de **factores de error** binarios: nunca uniforme; usa el prior informativo moderado de «Verosimilitudes» (`P(error) ≈ 0.2`–`0.3`). *Por qué:* un uniforme sobre los `2^k` perfiles (o sobre `{presente, ausente}` de cada factor) equivale a afirmar que cada error tiene un 50 % de probabilidad a priori de estar presente; no es neutral y sesga las primeras preguntas hacia el falso positivo (errores que el alumno no tiene mostrados como «indeterminados» o «probables»).
- Si las hipótesis son jerárquicas, asígnales valores `theta` ordenados y centrados.
- Si el docente no fija valores, usa una escala simétrica centrada en 0.
- La escala `theta` es fija y depende solo del número de hipótesis, no del banco de preguntas. Con `n` hipótesis jerárquicas, usa valores centrados en `0` con intervalos de `2`: `theta_i = 2 * (i - 1) - (n - 1)`, es decir, `theta` recorre `{-(n-1), ..., +(n-1)}` y `theta_max = n - 1`. Ejemplos: `n = 2` → `{-1, +1}`; `n = 3` → `{-2, 0, +2}`; `n = 4` → `{-3, -1, +1, +3}`; `n = 5` → `{-4, -2, 0, +2, +4}`.
- Sitúa las dificultades dentro de la mitad central de esa escala: `b_q` debe quedar en `[-theta_max / 2, +theta_max / 2]`. Como `theta_max` depende de `n`, la conversión de dificultades también depende de `n`, no solo del número de categorías.
- Si el docente da `k` categorías cualitativas de dificultad, repártelas uniformemente en ese intervalo: `b_j = (theta_max / 2) * (2 * (j - 1) / (k - 1) - 1)` para `j = 1..k` (si `k = 1`, usa `b = 0`). Ejemplos: `n = 3` y `k = 3` → `{-1, 0, +1}`; `n = 3` y `k = 5` → `{-1, -0.5, 0, +0.5, +1}`; `n = 4` y `k = 3` → `{-1.5, 0, +1.5}`; `n = 2` y `k = 5` → `{-0.5, -0.25, 0, +0.25, +0.5}`.
- No uses una tabla de dificultades fija e independiente de `n`: con pocas hipótesis y muchas categorías produciría dificultades fuera del rango de niveles (por ejemplo, `n = 2` con `b = ±2`) y anularía la separación entre escalas.
- Si el docente da valores numéricos de `b_q` fuera del intervalo, recórtalos (clamp) al intervalo.
- No recalcules nunca `theta` a partir de los extremos del banco. Una sola pregunta atípicamente difícil o fácil no debe redefinir la escala: si estiras `theta` para acomodarla, saturas las verosimilitudes del resto del banco (todas las probabilidades quedan pegadas a `c_q` o a `1`) y el posterior da saltos sobreconfiados con una sola respuesta.
- Si la mayoría de las dificultades del banco quedara fuera del intervalo, no estires la escala: revisa con el docente la definición de niveles y dificultades, porque el diseño es incoherente.
- Mantén entre recursos el invariante de comparabilidad `a_ef * Δtheta = 2.5` (con `a_ef = 1.25` e intervalos de `2` entre hipótesis adyacentes); con `n = 2` compensa además con más preguntas o define la escala desde una probabilidad objetivo `P*`. *Qué garantiza y qué no:* el invariante iguala la **pendiente máxima** de la ICC entre formatos para cualquier `n`, pero la comparabilidad de confianzas y velocidades es estricta solo entre recursos con el mismo `n` — el margen entre el nivel extremo y el ítem más difícil es `(n - 1) / 2`, y con `n = 2` los ítems extremos confirman débilmente (P ≈ 0.65 en abierta, ≈ 0.77 en 4 opciones) —. Tampoco iguala la fuerza máxima de la evidencia de un fallo: en el cociente de verosimilitudes de fallo el factor `(1 - c)` se cancela y la razón tiende a `e^(a * Δtheta)` con la `a` **nominal** (≈ 12 en abierta, ≈ 28 en 4 opciones, ≈ 148 en verdadero/falso con `Δtheta = 2`); esos saltos los acota el techo de dominio de «Verosimilitudes».

## Actualización bayesiana

Tras cada respuesta:

1. calcula la verosimilitud de esa respuesta bajo cada hipótesis;
2. multiplica prior por verosimilitud;
3. normaliza;
4. usa el resultado como nuevo estado.

Esto debe hacerse después de cada interacción relevante.

## Elección del modelo

- Si la finalidad principal es estimar un nivel ordenado de dominio, usa hipótesis ordinales e IRT 3PL.
- Si la finalidad principal es identificar una estrategia o error excluyente, usa hipótesis nominales con verosimilitudes explícitas por pregunta.
- Si varios errores, habilidades o necesidades pueden coexistir, usa dimensiones separadas o perfiles completos. La IA decide la arquitectura: usa dimensiones separadas cuando cada factor se interpreta y se corrige por separado; usa perfiles completos cuando la respuesta esperada cambia por combinaciones de factores, un error enmascara otro o la intervención pedagógica depende de la combinación. Si `2^k` perfiles es inviable, agrupa factores relacionados o diagnostica por fases.
- Si el recurso debe estimar nivel y diagnosticar errores, combina una distribución ordinal global con distribuciones diagnósticas paralelas y organízalas en **bloques pedagógicos** (`nivel`, `errores`, `categorías`, etc.). No preguntes al docente por pesos técnicos: infiérelos de la finalidad expresada.
- No fuerces errores coexistentes dentro de una escala ordinal única.

## Verosimilitudes

- Si las hipótesis representan niveles ordenados de dominio, usa IRT 3PL.
- Fórmula recomendada:

`P(acierto | H_i, q) = c_q + (1 - c_q) / (1 + exp(-a * (theta_i - b_q)))`

- Usa por defecto:
  - `a_ef = 1.25` (discriminación efectiva objetivo)
  - `a = a_ef / (1 - c_q)`
  - `c_q = 1 / m_q` si hay azar
  - `c_q = 0` si no lo hay
- No fijes `a` directamente: fija la discriminación efectiva objetivo `a_ef = 1.25` y calcula `a` por pregunta con `a = a_ef / (1 - c_q) = 1.25 / (1 - c_q)`.
  - Hazlo **siempre**, aunque todas las preguntas tengan el mismo número de opciones. Esta regla iguala la pendiente máxima de la ICC, no garantiza que todos los formatos aporten la misma información esperada. Un `a` fijo con distintos `c_q` produce pendientes reales distintas y no comparables (por ejemplo, `a=1.5` fijo da `a_ef=1.0` con 3 opciones pero `a_ef=1.125` con 4). La selección por ganancia de información seguirá favoreciendo los ítems que aporten más evidencia.
  - `a_ef = 1.25` garantiza que `a` se mantenga dentro del rango habitual en psicometría (0.5–2.5) para cualquier formato de 2 o más opciones: el caso extremo, verdadero/falso (`c_q=0.5`), da exactamente `a = 2.5`.
  - Valores que debes obtener: abierta (`c_q=0`) → `a=1.25`; 5 opciones (`c_q=0.20`) → `a=1.5625`; 4 opciones (`c_q=0.25`) → `a≈1.667`; 3 opciones (`c_q=1/3`) → `a=1.875`; verdadero/falso (`c_q=0.5`) → `a=2.5`.
- Aplica un **techo de dominio** también en el caso ordinal: acota `P(acierto | H_i, q) <= 0.95` (equivalentemente, `P(fallo) >= 0.05`) para toda hipótesis, incluido el nivel más alto en ítems fáciles. El 3PL puro deja que `P(acierto) → 1` en ítems fáciles con mayor pseudoazar, de modo que un solo fallo dispara el posterior casi de forma determinista (con `c = 0.5` la razón de verosimilitud de un fallo entre niveles adyacentes llega a ≈ 148, frente a ≈ 12 en abierta). El techo modela el descuido (*slip*), que el 3PL no contempla, y alinea el caso ordinal con el nominal, que ya impone `0.9`–`0.95`, nunca `1`. Usa `0.90` si quieres ser más conservador.
- Si el alumno falla:

`P(fallo | H_i, q) = 1 - P(acierto | H_i, q)`

- Si las hipótesis no son jerárquicas, distingue dos casos.
- Si son **alternativas excluyentes** (por ejemplo, estrategia A / estrategia B / dominio correcto), no uses IRT logística. Genera para cada pregunta un vector de `n` verosimilitudes `P(acierto | H_i, q)`, una por hipótesis.
- Si los errores o necesidades **pueden coexistir**, no los metas en una sola distribución nominal. Modela una dimensión por factor (`error largo`, `error cero`, etc.) o, de forma equivalente, una distribución sobre **perfiles completos** (`2^k` combinaciones posibles de `k` factores).
- **Prior de los factores de error: no uniforme.** Asigna a cada factor una probabilidad a priori baja de estar presente (por defecto `P(error) ≈ 0.2`–`0.3`), nunca el uniforme `0.5`. El recurso aplica este valor de forma automática; el docente puede ajustar la prevalencia de su grupo si lo desea, pero no está obligado. *Por qué:* los errores conceptuales suelen ser minoritarios; el uniforme no es neutral (afirma que cada alumno tiene cada error con probabilidad `0.5`) y produce falsos positivos en las primeras preguntas.
- **Ajusta ese prior con lo que el docente ya te ha dicho, sin preguntarle números.** Si al describir el recurso el docente califica la frecuencia de un error, tradúcelo tú a un prior; no le pidas una prevalencia numérica ni le muestres el valor elegido en la interfaz del alumno.

  | Cómo lo describe el docente | `P(error)` inicial |
  |---|---|
  | «muchos», «la mayoría», «les pasa siempre», «muy frecuente» | `0.40` |
  | «algunos», «a veces», «bastantes», o no dice nada | `0.20`–`0.30` (defecto) |
  | «pocos», «casos aislados», «alguno suelto», «raro» | `0.10`–`0.15` |

  Reglas que acotan la heurística:
  - **Nunca `≥ 0.5`, nunca `< 0.10`.** Por encima de `0.5` el prior afirma que el error es más probable que su ausencia, que es el sesgo que este apartado corrige. Por debajo de `0.10` harían falta `3` fallos discriminantes para confirmar un error real, y en un banco pequeño puede no confirmarse nunca.
  - **La muestra mínima no se relaja jamás, y con `0.40` es lo único que protege.** Desde `0.40`, un solo fallo discriminante (`LR ≈ 4`) lleva la marginal a `0.727` y cruza el umbral de «presente»: sin exigir la muestra mínima de evidencia, la palabra del docente bastaría para diagnosticar al alumno. Mantén los `2` intentos por factor.
  - **El prior es también el ancla del olvido.** Un factor con `P(error) = 0.40` que se quede sin evidencia reciente no vuelve a `0.25`, vuelve a `0.40`, y reaparecerá como «indeterminado». Es coherente: el docente dijo que ese error es frecuente en su grupo.

  *Por qué:* el ajuste es deliberadamente suave. Mueve la decisión **un ítem**, no la predetermina: confirmar un error exige `2` fallos discriminantes desde el prior por defecto, `1` desde `0.40` y `3` desde `0.10`. El prior por sí solo no puede declarar un error **presente** en ningún punto del rango permitido. El caso que corrige es el falso negativo simétrico al que motivó el prior informativo: cuando el docente ya sabe que un error es frecuente en su grupo, partir de `0.25` gasta preguntas en redescubrirlo.
- En ese caso multifactorial, cada pregunta debe definir cómo responde cada perfil. Lo mínimo es una probabilidad de acierto por perfil; mejor aún, una distribución por opción `P(R = r | perfil, q)` para aprovechar qué distractor ha elegido el alumno, no solo si acertó o falló.
- Si partes de factores simples, asigna cada valor respondiendo: «si el alumno tuviera este error, ¿con qué probabilidad acertaría esta pregunta?». Bajo si la pregunta ataca el concepto que ese error distorsiona; alto si el error no interfiere.
- Acota cada valor: no por debajo del suelo de azar `1/m` (m opciones), salvo la excepción del punto siguiente; la hipótesis o perfil de dominio en torno a `0.9`–`0.95`, nunca `1`.
- Si un distractor concreto es la respuesta que produce un error, la probabilidad de **esa opción** debe subir bajo ese perfil, y la de acierto puede quedar cerca del suelo o por debajo: el alumno es atraído activamente hacia esa respuesta equivocada.
- No afines el decimal: usa tramos (`≈0.9` no afecta / `≈0.5` afectación parcial / `≈0.15–0.25` distractor que captura el error / `≈1/m` suelo si falla por azar). Lo importante es que los perfiles o factores correctos se separen claramente en las preguntas que discriminan.
- No uses tablas fijas globales si cada pregunta puede generar sus propias verosimilitudes.
- La calidad del diagnóstico no depende solo del algoritmo: depende también de cómo estén definidas las hipótesis, categorías, dificultades, conceptos y errores. Si esas clasificaciones están mal conformadas, si los errores relevantes no están bien identificados o si el banco cubre mal los casos importantes, las verosimilitudes generadas pueden representar mal la realidad y sesgar la adaptación.
- En el diagnóstico final no calcules una `theta` esperada (no tiene sentido sin orden). Si el modelo es nominal excluyente, puedes reportar la hipótesis MAP y su probabilidad. Si el modelo es multifactorial, reporta por cada factor si queda **presente**, **ausente** o **indeterminado**, con su probabilidad marginal o confianza asociada.
- Con prior informativo (`P(error) ≈ 0.2`–`0.3`), la ausencia arranca ya en `0.7`–`0.8` sin evidencia alguna: no declares un factor **ausente** solo porque su marginal supere el umbral de confianza. Exige además su muestra mínima de evidencia y distingue en el reporte «ausente confirmado» (con evidencia) de «sin evidencia suficiente» (el valor por defecto del prior).

## Respuestas con crédito parcial

- Si una respuesta no es solo acierto o fallo, sino que admite grados (varios pasos, componentes ponderados, aciertos parciales), resúmela en una puntuación `s` entre `0` y `1`.
- Si solo tienes una puntuación parcial agregada `s`, construye una verosimilitud geométrica:

`L(H_i) = P(acierto | H_i, q)^s * P(fallo | H_i, q)^(1 - s)`

- Usa esta `L(H_i)` en la actualización bayesiana en lugar de elegir entre `P(acierto)` y `P(fallo)`. La normalización y el resto del proceso no cambian.
- Casos límite: `s = 1` equivale a acierto pleno; `s = 0` a fallo pleno. Un `s = 0.5` no es necesariamente neutro: favorece las hipótesis para las que el ítem predice una puntuación intermedia.
- Si el ítem tiene `J` componentes aproximadamente independientes y `s` es la fracción ponderada de componentes correctos, puedes conservar la fuerza de la evidencia usando `L(H_i) = P(acierto | H_i, q)^(sJ) * P(fallo | H_i, q)^((1 - s)J)`.
- Cuidado: el exponente `J` trata la respuesta como `J` ensayos independientes con la **misma** probabilidad `p_i` del ítem completo, así que solo es razonable si los componentes son de **dificultad parecida**. Si difieren claramente en dificultad (lo habitual en tareas por pasos), esta forma **sobrecuenta** la evidencia frente al modelo por componentes; en caso de duda, usa un `J` menor que el número real de componentes (evidencia más conservadora).
- Si tienes evidencia separada por componente, es preferible multiplicar las verosimilitudes de cada componente en lugar de reducir todo a una sola `s`.
- Define cómo se calcula `s` de forma explícita y autocorregible: suma ponderada de subcriterios, fracción de pasos correctos, cercanía a la solución numérica, etc. Los pesos deben sumar `1`.
- No trates como binaria una respuesta que admite grados: pierdes información diagnóstica.
- **Calcula la ganancia de información con la misma verosimilitud con la que vas a actualizar.** Esta es la regla; lo demás se deduce de ella.
- Regla operativa, por orden de preferencia:
  1. **Si conoces los componentes de la respuesta, no la resumas en `s`.** Actualiza multiplicando las verosimilitudes de cada componente (como ya se dice arriba) y calcula la ganancia promediando sobre las combinaciones de resultados de los componentes. Es el caso mejor: selección y actualización comparten modelo.
  2. **Si solo dispones de la `s` agregada**, actualiza con la verosimilitud geométrica y calcula la ganancia promediando sobre los **dos extremos** (`s = 0` y `s = 1`) con `P(acierto | H_i, q)`. Eso es exactamente la ganancia del modelo binario que la geométrica extiende, y es la elección coherente.
  3. **No promedies la ganancia sobre la distribución real de `s` mientras actualizas con la geométrica.** Parece más fino y es peor: ver el porqué.
- *Por qué:* la verosimilitud geométrica manda toda puntuación intermedia hacia las hipótesis intermedias (por diseño: se maximiza en `p_i = s`). Un ítem de dificultad media produce puntuaciones intermedias con **cualquier** alumno, así que concentra el posterior en la hipótesis del medio sea cual sea el estado real. Si calculas la ganancia sobre la distribución verdadera de `s` pero actualizas con la geométrica, el selector detecta esa concentración, la interpreta como información y prefiere justamente esos ítems: la confianza sube y el acierto baja. Medido sobre un recurso real de crédito parcial (7 subcriterios ponderados, 3 hipótesis, banco de 39 ítems por tipo, 4 preguntas por sesión, 3 semillas): la regla actual acierta el **98.5 %**; promediar sobre la distribución exacta de `s` manteniendo la geométrica baja al **95.9 %**, y hacerlo sobre cuatro escenarios discretos (`0`, parcial bajo, parcial alto, `1`) baja al **93.7 %**. El uso de ítems de dificultad media pasa del `9 %` al `27 %`. En cambio, pasar al modelo por componentes del punto 1 **sube** al `99.3 %` y corrige de paso una infra-confianza crónica de la geométrica (asigna `0.75` de probabilidad a la hipótesis verdadera cuando acierta el `98 %` de las veces; por componentes, `0.99`). Comprobado también con componentes fuertemente dependientes entre sí: el modelo por componentes sigue ganando (`97.3 %` frente a `94.4 %`) y no llega a sobrecontar evidencia.

## Suelo de azar en ítems compuestos

- Si un ítem se corrige por varios componentes con distinto número de opciones y se puntúa con crédito parcial, el suelo agregado no es la probabilidad de acertar el ítem completo, sino la puntuación parcial esperada por azar.
- Calcula ese suelo de puntuación esperada como media ponderada de los azares de cada componente:

`c_q = Σ_j w_j * c_j`  con  `c_j = 1 / m_j`  y  `Σ_j w_j = 1`

- Usa ese `c_q` agregado en la función logística solo cuando la ICC represente la puntuación esperada del ítem compuesto.
- Si el ítem compuesto se corrige como todo-o-nada, no uses la media ponderada: la probabilidad de acierto pleno por azar es el producto `Π_j c_j` si los componentes se aciertan independientemente.
- Los pesos `w_j` deben coincidir con los que uses para calcular la puntuación `s` del crédito parcial.

## Diagnóstico multidimensional

- Si necesitas saber no solo el nivel global sino qué habilidades o pasos fallan, mantén varias distribuciones bayesianas en paralelo: una por categoría o nivel y otra por cada dimensión diagnóstica (habilidad, paso, tipo de error).
- Actualiza cada distribución con la evidencia que le corresponde: el resultado global puede alimentar la creencia de nivel; cada subcriterio debe alimentar solo su dimensión. No uses el mismo acierto/fallo global para actualizar varias dimensiones independientes si la pregunta exige varias habilidades a la vez, porque duplicas evidencia y atribuyes mal la causa del error.
- Cada dimensión puede tener su propio suelo de azar `c` según su número de opciones, por lo que sus porcentajes no son directamente comparables entre sí. En dimensiones ordinales, la referencia común es el valor latente `theta`; en factores nominales de error no calcules `theta`: reporta probabilidades marginales, estado (`presente`, `ausente`, `indeterminado`) y muestra mínima de evidencia.
- No metas en una sola distribución dimensiones que pueden coexistir: usa distribuciones separadas.
- Si varias dimensiones diagnósticas interactúan de manera fuerte, sustituye las distribuciones independientes por una sola distribución sobre perfiles completos. Usa perfiles completos cuando la respuesta esperada cambia por combinaciones de factores, cuando un error enmascara otro o cuando la intervención depende de la combinación; usa dimensiones separadas cuando los factores se evidencian e interpretan de forma razonablemente independiente. No preguntes al docente por esta decisión en términos técnicos: dedúcela de la descripción pedagógica de los errores.
- El nivel por categoría guía qué practicar; el diagnóstico por dimensión guía qué explicar o reforzar.
- Si combinas una distribución ordinal de nivel con factores de error (modelo combinado), ambos son estimaciones marginales paralelas alimentadas por la misma evidencia, no hallazgos independientes. Agrúpalos por bloques pedagógicos para la selección (`nivel`, `errores`, `categorías`), comprueba la coherencia del resultado final y, si el nivel estimado es alto y algún error queda «presente», preséntalo como matiz del nivel («domina X, aunque persiste el error Y»), no como conclusiones contradictorias yuxtapuestas.

## Preguntas y actividades

Cada pregunta o interacción autocorregible debe tener, cuando proceda:

- texto o enunciado;
- dificultad `b_q`;
- número de opciones `m_q`;
- categoría o concepto;
- criterio de corrección;
- ayuda o pista opcional;
- retroalimentación mínima tras la respuesta;
- explicación específica, especialmente si la finalidad principal es aprendizaje, práctica o refuerzo.

**Cuándo mostrar la corrección depende del modo.** En modo `Práctica` o de aprendizaje, muestra acierto/fallo y explicación tras cada respuesta: el objetivo es aprender y la estimación es viva. En modo `Diagnóstico`, si todos los ítems miden el mismo constructo (una sola distribución nominal, o de nivel cuando el ítem transparenta cuál es la respuesta de dominio), **no reveles acierto/fallo ni explicación por ítem**: da una confirmación neutra y **agrupa las soluciones al final**, con el diagnóstico ya cerrado. *Por qué:* revelar la respuesta correcta enseña la hipótesis diagnosticada (el modelo correcto, la estrategia buena) en mitad de la sesión y arrastra las respuestas posteriores hacia ella. Es una contaminación distinta de la del ítem reutilizado (§ «Selección adaptativa»): aquí no se repite el ítem, sino que el feedback de uno contamina a los demás, porque todos preguntan por lo mismo. La retroalimentación no se suprime, se **pospone**: cierra siempre con las soluciones comentadas.

Si el recurso es procedural o tutorial, las interacciones pueden no ser preguntas clásicas, pero deben seguir siendo autocorregibles o evaluables de forma explícita.

### Bancos generados: variantes parametrizadas

Si el banco genera los ítems a partir de plantillas (mismo concepto, dificultad y formato con datos distintos), aplica estas reglas. Sin ellas un banco generado no es más fiable que uno escrito a mano: es menos fiable, porque nadie ha leído la mayoría de sus ítems.

- **Deriva la respuesta correcta, no la transcribas.** La plantilla debe calcular la solución aplicando la propia regla que el ítem enseña sobre los parámetros sorteados (para `b^m · b^n`, calcular `b^(m+n)`). Así solo hay una regla que revisar por plantilla, en lugar de una respuesta por variante que pueda estar mal copiada, y la corrección de todas las variantes se sigue de la corrección de esa regla.
- **Mantén fijos por plantilla los metadatos que alimentan el modelo**: dificultad `b_q`, número de opciones `m_q`, categoría, factor de error y posición de la opción distractora. No los sortees. Así todas las variantes de una plantilla son equivalentes bajo el modelo, y la validación Monte Carlo del banco (que se ejecuta sobre las plantillas) sigue siendo aplicable a los ítems que ve el alumno.
- **Verifica cada variante de forma automática**, antes de entregar y sobre muchas variantes por plantilla. Como mínimo: (1) la respuesta marcada como correcta reproduce el valor de la expresión del enunciado, evaluada numéricamente en valores de prueba **lejos de `0` y de `1`**, donde muchas igualdades falsas se cumplen por casualidad; (2) las opciones son distintas entre sí, y ninguna opción incorrecta tiene el mismo valor que la correcta, porque eso deja la pregunta sin respuesta única; (3) enunciado, pista, explicación y opciones se representan sin error. Cuando una variante incumpla alguna condición, vuelve a sortear los parámetros en lugar de entregarla.
- **La verificación numérica prueba la matemática, no la redacción.** Un enunciado puede ser cierto y aun así haber perdido la pregunta: si la plantilla simplifica la expresión antes de mostrarla, puede acabar enseñando la respuesta (`a^0` presentado ya como `1`). Ninguna comprobación numérica detecta eso. Lee una muestra de variantes de cada plantilla antes de dar el banco por bueno.
- Comprueba que cada plantilla admita **variantes suficientes** para la longitud prevista de una sesión. Una plantilla con dos o tres variantes vuelve a producir repeticiones y con ellas la contaminación del feedback que las variantes venían a evitar.

## Selección adaptativa

Para cada candidata disponible:

1. calcula la probabilidad marginal de acierto;
2. simula posterior si hay acierto;
3. simula posterior si hay fallo;
4. calcula la entropía esperada posterior;
5. calcula la ganancia esperada de información.

Selecciona la candidata con mayor ganancia esperada de información cuando la finalidad principal sea diagnóstica y el objetivo sea estimar un nivel global.

Si el estado son varias distribuciones paralelas (factores de error o dimensiones diagnósticas), calcula la ganancia esperada de cada distribución y agrúpala por **bloques pedagógicos**. Dentro de cada bloque puedes sumar las ganancias de sus distribuciones (`IG_bloque = Σ IG_d`), porque la entropía conjunta factorizada es la suma de entropías. Para combinar bloques, normaliza cada uno entre las candidatas disponibles (`IG_bloque_norm(q) = IG_bloque(q) / max IG_bloque`) y usa pesos automáticos según la finalidad. Valores por defecto: si la finalidad se centra en un bloque, `w = 0.7` para ese bloque y `0.3` repartido entre los demás; si es mixta, pesos iguales por bloque (`w_b = 1 / número de bloques`), no por número bruto de dimensiones. Un bloque está **decidido** cuando alcanza su criterio de confianza: el de nivel, cuando `max(p_i) >= p_min` con el mínimo de preguntas cumplido; el de errores, cuando todos sus factores están decididos (marginal fuera de la zona indeterminada, con su muestra mínima). Cuando un bloque queda decidido, reparte su peso proporcionalmente entre los bloques aún inciertos. No pidas estos pesos al docente. Promedia sobre los resultados que el ítem modele (por opción, si hay distractores diagnósticos).

Tres cautelas con esta utilidad combinada:

- no está en bits: la normalización reescala el mejor candidato de cada bloque a `1` aunque sus ganancias sean minúsculas, así que el criterio de parada «la mejor pregunta aporta muy poca información» debe evaluarse sobre la **IG cruda total** (en bits), nunca sobre la utilidad normalizada;
- por lo mismo, un bloque casi agotado puede quedar sobrerrepresentado justo antes de cruzar su criterio de «decidido»; si eso resulta visible, pondera las ganancias crudas del bloque (usando la media por dimensión en lugar de la suma) o normaliza por la entropía restante del bloque en vez de por el máximo;
- la suma entre bloques es exacta para la creencia factorizada que mantiene el sistema, no para el posterior conjunto verdadero: cuando varias distribuciones se actualizan con evidencia compartida, sus marginales están correlacionadas y la suma ignora esa redundancia. Trátala como indicador de agotamiento del banco, no como información conjunta, y no compongas confianzas marginales en una probabilidad conjunta. Consulta `matematicas.html §10.6` (https://jjdeharo.github.io/recursos-adaptativos/matematicas.html#s10-6).

En recursos de práctica adaptativa o refuerzo con varias categorías, tipos de problema o conceptos, usa una selección en dos fases:

1. **Fase diagnóstica inicial.** Hasta que cada categoría relevante tenga una muestra mínima de intentos, prioriza las categorías con menos evidencia. Dentro de ellas, usa la ganancia esperada de información para elegir la pregunta más diagnóstica. Un valor por defecto razonable es exigir al menos `2` intentos por categoría antes de salir de esta fase. Ten presente que `2` es el mínimo defendible, no un valor cómodo: con olvido activo la marginal por categoría es volátil, así que sube la muestra mínima si el banco lo permite. Si hay muchas categorías, esta fase puede consumir la sesión (con `10` categorías y `2` intentos son ya `20` preguntas): agrupa categorías afines en bloques o reduce la muestra mínima para que el diagnóstico inicial no supere el máximo práctico.
2. **Fase de refuerzo.** Cuando todas las categorías relevantes tengan muestra mínima, prioriza la categoría con menor dominio estimado. Dentro de esa categoría, no elijas automáticamente la pregunta más difícil: selecciona una pregunta informativa y cercana al nivel estimado del alumno. Una regla razonable es `utilidad = α * IG_norm + (1 - α) * ajuste`, con las dos escalas definidas en `[0, 1]`: `IG_norm = IG(q) / max IG` entre las candidatas del momento, y `ajuste = max(0, 1 - |b_q - E[theta]| / 2)`, que vale `1` cuando la dificultad coincide con el nivel estimado (`E[theta] = Σ p_i * theta_i`) y `0` cuando se aleja un intervalo completo de nivel. Sin definir ambas escalas en el mismo rango, el peso `α` no significa nada.

Para que ese `ajuste` signifique algo, **cada categoría debe cubrir el rango de dificultades por sí sola**, no solo el banco en su conjunto. Si una categoría no tiene ningún ítem cerca del extremo superior del rango, `ajuste` vale `0` en todas sus candidatas para un alumno situado en el nivel más alto, la utilidad se reduce a la ganancia de información y el término de adecuación deja de existir justo para los alumnos a los que debía proteger; lo mismo ocurre en el extremo inferior con las categorías sin ítems fáciles. Ten presente que, con las dificultades confinadas a la mitad central de la escala, el mejor `ajuste` alcanzable en un nivel extremo ya es solo `1 - theta_max / 4` (con `n = 4`, `0.25`): eso es lo esperable; un `0` no lo es. Antes de entregar, tabula la cobertura de categorías por dificultad y comprueba que ninguna casilla extrema queda vacía.

No uses la entropía de Shannon como único criterio permanente cuando la finalidad principal sea practicar o reforzar. Shannon indica dónde hay más incertidumbre diagnóstica; el refuerzo debe atender también, y preferentemente, a lo que el alumno domina menos.

En tests adaptativos de diagnóstico global con criterio de parada, no es obligatorio aplicar la fase de refuerzo. En ese caso basta con maximizar la información esperada, diversificando categorías en empates o cuando varias candidatas tengan utilidad equivalente.

Ten en cuenta que maximizar la información esperada tiende a proponer preguntas con probabilidad de acierto cercana al `50 %`. Con alumnado joven o con dificultades, puedes abrir con una pregunta asequible o intercalar alguna de éxito probable: pierdes algo de eficiencia informativa a cambio de sostener la motivación. Es una decisión pedagógica opcional.

Si varias son prácticamente equivalentes:

- rompe empates con aleatorización;
- favorece categorías o conceptos menos repetidos.

No uses selección determinista simple en empates.

Evita repetir la misma pregunta de forma mecánica:

- no repitas exactamente el mismo ítem de manera consecutiva, salvo que el diseño pida de forma explícita un reintento inmediato;
- aplica penalización por frecuencia o una ventana de exclusión reciente para que un ítem ya usado pierda prioridad durante varias selecciones;
- si varias candidatas tienen utilidad parecida, prefiere la menos reciente y la menos repetida;
- solo permite reusar un ítem cuando el banco sea pequeño, no existan alternativas comparables o el objetivo pedagógico sea revisar de forma deliberada ese mismo caso.

No confundas este problema con un simple criterio de desempate:

- la aleatorización solo ayuda si existen varias candidatas razonables;
- para evitar repeticiones hace falta redundancia local en el banco: varias preguntas alternativas por categoría, nivel de dificultad, tipo de ítem o error relevante;
- si en una zona diagnóstica solo hay un ítem útil, la IA debe reconocer que el banco es insuficiente para una adaptación variada en esa zona;
- en ese caso no simules variedad con una falsa aleatorización: reutiliza el ítem solo cuando sea necesario, cambia temporalmente de objetivo pedagógico o deja el resultado como limitado por el tamaño del banco.

Evidencia de un ítem reutilizado:

- si el ítem se reutiliza después de que el alumno viera su corrección o explicación (incluido el reintento inmediato), el acierto posterior no es evidencia plena de dominio: puede reflejar solo memoria del feedback;
- **en modo `Práctica`, trátalo siempre como las pistas: crédito parcial, nunca exclusión de la actualización.** El acierto recibe `s` reducido (tanto menor cuanto más explícita fue la explicación mostrada) y el fallo cuenta completo (`s = 0`): fallar un ítem cuya corrección ya se vio es evidencia clara de no dominio. *Por qué:* la práctica es abierta y el banco finito, así que antes o después todo ítem disponible se repetirá; si los repetidos no actualizan, al agotarse los ítems nuevos de la categoría menos dominada la estimación se congela, esa categoría sigue siendo la prioritaria y el selector entra en un bucle de repasos sin efecto, mientras el olvido degrada el estado sin que ninguna evidencia lo compense. Excluirlos violaría además la regla de diseño de que cada respuesta modifica el estado estimado;
- solo en modo `Diagnóstico` (donde los ítems no deben repetirse salvo un reintento inmediato deliberado) puedes excluir el reintento de la actualización y usarlo solo como práctica: la sesión es corta y su cierre no depende de esa evidencia;
- la mejor redundancia local no es repetir el mismo ítem, sino disponer de **variantes parametrizadas** del mismo tipo (mismo concepto, dificultad y formato con datos distintos): cada variante cuenta como ítem nuevo y no arrastra la contaminación del feedback.

## Criterio de parada

Detén la sesión cuando se cumplan criterios razonables de cierre, por ejemplo:

- mínimo de preguntas ya cumplido;
- entropía por debajo de `H_stop`;
- hipótesis más probable por encima de `p_min`;
- no quedan preguntas útiles;
- la mejor pregunta restante aporta muy poca información;
- se alcanza el máximo práctico.

Si usas `p_min`, calcula el umbral orientativo:

`H_stop = -p_min * log2(p_min) - (1 - p_min) * log2((1 - p_min) / (n - 1))`

Tras cumplir el mínimo de preguntas, aplica **uno** de estos dos cierres de confianza:

- **Pocas hipótesis** (`n <= 4`, lo habitual): cierra cuando `max(p_i) >= p_min` (por defecto `0.80`).
- **Muchas hipótesis**, donde exigir `0.80` es poco práctico: cierra cuando `max(p_i)` alcance un valor moderado (por ejemplo `>= 0.50`) **y** la ganadora se separe de la segunda: `P(ganadora) - P(segunda) >= Δ_min`, con `Δ_min ≈ 0.3`–`0.4`.

No combines comprobaciones redundantes creyendo que añaden exigencia. *Por qué:* cuando `H_stop` se deriva del mismo `p_min` (fórmula anterior), `max(p_i) >= p_min` ya implica `H <= H_stop`; y con `p_min = 0.80` la separación ya es `>= 0.60`, así que añadirle un `Δ_min` de `0.3`–`0.4` es inerte (solo añadiría exigencia si `Δ_min > 2 * p_min - 1`). La separación es una **alternativa** a un `p_min` alto, no un añadido. Con `n = 2` ambas son equivalentes (`sep = 2 * max - 1`).

En modelos multifactoriales, evalúa la parada **por factor**: un factor queda decidido cuando su marginal sale de la zona indeterminada (por ejemplo, `P(error) >= 0.7` presente, `<= 0.3` ausente) y tiene su muestra mínima de evidencia. Cierra cuando todos los factores estén decididos, cuando ningún ítem aporte ganancia apreciable sobre los indeterminados o al alcanzar el máximo práctico; los factores sin decidir se reportan como indeterminados, no se fuerzan.

Si se cierra por máximo de preguntas, banco agotado o utilidad marginal baja sin alcanzar el criterio de confianza elegido, presenta el resultado como provisional.

Reglas mínimas:

- no cierres demasiado pronto;
- no alargues artificialmente la sesión cuando la utilidad marginal ya es baja;
- si la incertidumbre sigue siendo alta, el resultado debe indicarse como provisional.

## Refuerzo continuo sin parada

- En recursos de práctica o refuerzo abierto puede no haber criterio de parada: la sesión continúa mientras el alumno practique.
- En ese modo, el estado estimado no es un diagnóstico cerrado, sino una estimación viva que se actualiza con cada respuesta.
- No apliques `H_stop` ni `p_min` para cerrar la sesión; úsalos, si acaso, solo para informar del grado de confianza alcanzado.
- Mantén la selección en dos fases durante toda la sesión: diagnóstico mínimo por categoría y, después, refuerzo de lo menos dominado.
- El estado del alumno puede cambiar mientras practica: aplica olvido exponencial para que la estimación siga su estado actual. Antes de cada actualización, atenúa el posterior **hacia el prior** `pi_i` y renormaliza: `p_i <- p_i^lambda * pi_i^(1 - lambda)` (dividido por la suma). Con prior uniforme, esto coincide con la forma simple `p_i <- p_i^lambda / Σ_j p_j^lambda`.
- **No atenúes hacia la uniforme cuando el prior sea informativo.** La forma simple tiene la uniforme como punto fijo: un factor de error con prior `P(error) ≈ 0.25` que pase un tiempo sin recibir evidencia deriva solo hacia el 50 % (≈ 0.40 tras 20 pasos con `lambda = 0.95`) y reaparece como «indeterminado» o «probable» sin que el alumno haya hecho nada — el mismo falso positivo que el prior informativo evita. Anclado al prior, el olvido descarta la evidencia antigua (la de hace `k` pasos pesa `lambda^k`) pero el prior conserva siempre peso completo, y una distribución sin evidencia nueva permanece en su prior en lugar de degradarse.
- Aplica la atenuación a cada distribución en cada paso de la sesión, también a las que no reciben evidencia en esa respuesta: así todas siguen el paso del tiempo y, gracias al anclaje, las no observadas vuelven a su prior, no a la uniforme.
- Fija primero la memoria efectiva `M` en **intentos de la propia distribución** (por defecto `M = 20`), no en respuestas de la sesión, y deriva `lambda` de ahí. Si el estado es una sola distribución que se actualiza en cada respuesta, `lambda = 1 - 1/M` (con `M = 20`, `lambda = 0.95`, el rango habitual `0.9`–`0.98`).
- **Con varias distribuciones paralelas, calcula un `lambda` por distribución.** Al atenuarlas todas en cada respuesta, cada una envejece una vez por respuesta pero solo recibe evidencia cuando esa respuesta le corresponde. Si la distribución `d` se actualiza en `1` de cada `K_d` respuestas, un `lambda` común le dejaría una memoria de `M / K_d` intentos propios. Usa `lambda_d = (1 - 1/M)^(1 / K_d)`, donde `K_d` es el número medio de respuestas entre dos actualizaciones de `d` (`K_d = 1` para las dimensiones evaluadas en cada respuesta; `K_d = n` categorías si cada pregunta pertenece a una de `n` categorías). Ejemplo: con `M = 20` y `6` categorías, `lambda = 0.95` para una dimensión evaluada siempre y `lambda = 0.95^(1/6) ≈ 0.9915` para cada categoría. Aplicar el `0.95` también a las categorías les dejaría `20 / 6 ≈ 3.3` intentos de memoria y borraría el diagnóstico inicial (que suele tener `2` intentos por categoría).
- En recursos diagnósticos de sesión corta usa `lambda = 1` (sin olvido): ahí solo añadiría ruido.
- Con olvido activo, cuenta la muestra mínima por categoría o dimensión sobre una ventana reciente, no sobre toda la sesión: la evidencia caduca con el olvido, pero un contador acumulado no, y una categoría muestreada solo al principio seguiría contando como diagnosticada con su posterior ya degradado. La ventana de cada distribución dura lo que su memoria: los intentos dentro de las últimas `1 / (1 - lambda_d)` respuestas. Cuéntalos sin ponderar, para que los umbrales enteros conserven su significado: con peso exponencial, dos intentos consecutivos suman `1.95` y no cumplirían un umbral de `2`.
- Ese contador con caducidad gobierna las puertas de «muestra mínima» para afirmar dominio, no lo que se muestra al alumno: si la interfaz enseña cuántos ejercicios ha resuelto, ese número es el total real y no caduca.
- Si una categoría se queda sin evidencia dentro de la ventana, su creencia ya ha vuelto al prior: preséntala como **sin datos recientes**, no como una debilidad. Marcar en rojo lo que el modelo ya no sostiene es acusar al alumno de algo que no ha mostrado.
- Con olvido activo, presenta la confianza como referida al estado reciente del alumno.
- Si necesitas modelar explícitamente el aprendizaje (por ejemplo, mayor probabilidad de subir de nivel justo tras una explicación), usa un modelo de transición (Bayesian Knowledge Tracing); consulta `matematicas.html §3.5` (https://jjdeharo.github.io/recursos-adaptativos/matematicas.html#s3).

## Itinerarios por etapas

Si el recurso tiene fases, técnicas o etapas sucesivas:

- distingue entre estimación global y estimación local por etapa;
- no promociones una etapa usando solo la creencia global acumulada;
- decide la superación de la etapa con evidencia generada dentro de esa etapa.

Para dar una etapa por superada, conviene exigir al menos:

- confianza local suficiente;
- entropía local suficientemente baja;
- y un mínimo explícito de rendimiento observado en esa etapa, medido sobre evidencia **no** seleccionada por máxima información.

Cuidado con el porcentaje bruto de aciertos como criterio: si dentro de la etapa eliges los ítems por máxima ganancia de información, la tasa de acierto de todos los alumnos tiende por diseño hacia `(1+c)/2` (≈ 50 % sin azar, ≈ 62 % con cuatro opciones), así que un umbral fijo como «60 % de aciertos» puede bloquear a alumnos que sí dominan la etapa y su efecto depende del formato de las preguntas. Para medir el rendimiento de forma comparable, usa una de estas dos vías:

- **Ítems de salida (recomendado):** exige acertar 1-2 ítems de dificultad representativa del objetivo de la etapa, seleccionados **sin** criterio informativo (no por máxima IG). Al fijar la dificultad, el acierto sí informa sobre el dominio. El formato importa: evita verdadero/falso para los ítems de salida (un solo ítem V/F deja pasar por azar a la mayoría de quienes no dominan, `P(acierto | no dominio) ≈ 0.6`); con 4-5 opciones exige acertar los 2; con abierta ten presente que exigir 2 de 2 bloquea a ≈ 1 de cada 4 alumnos que sí dominan. El filtro de salida complementa la confianza local `p_min`, que ya criba: su función es cazar una calibración mala, no decidir en solitario.
- **Consistencia con el modelo:** exige que la tasa observada no quede muy por debajo de la esperada bajo la hipótesis de dominio local (es el ajuste de persona `l_z` de los fundamentos aplicado como criterio de etapa). Con los pocos ítems de una etapa la aproximación normal de `l_z` es débil: compara aciertos observados frente a esperados con un margen de ~1 desviación típica (o un test binomial exacto) y trátalo como señal orientativa, no como bloqueo duro.

Todo esto lo aplica el propio recurso de forma automática, a partir de las dificultades que ya conoce: no requiere que el docente conozca la metodología ni configure nada, salvo que quiera hacerlo.

Ejemplo razonable:

- `p_min = 0.80`
- acierto de 1-2 ítems de salida de dificultad representativa, en lugar de un umbral fijo de porcentaje de aciertos

Si el alumno repite una etapa:

- reinicia la estimación local de esa etapa, salvo justificación pedagógica explícita en contra.

Terminar una etapa no implica necesariamente haberla superado.

## Recuperación y refuerzo

- Si el alumno muestra dificultades, el sistema debe poder:
  - ofrecer pistas;
  - mostrar explicación;
  - proponer refuerzo;
  - cambiar el tipo de actividad;
  - reducir temporalmente la dificultad;
  - permitir reintento o repaso.
- Si muestra dominio, puede:
  - avanzar;
  - ampliar;
  - aumentar complejidad;
  - reducir ayuda.
- Efecto de las pistas en la evidencia: si el alumno acierta **después de una pista**, no lo registres como acierto pleno en la actualización bayesiana. Una pista sube la probabilidad de acierto de ese ítem, así que trátalo como crédito parcial con `s < 1` (tanto menor cuanto más determinante sea la pista; si la pista prácticamente da la respuesta, la evidencia de dominio es casi nula) y aplica la verosimilitud geométrica del crédito parcial. Los tiempos de respuesta y el uso de ayudas pueden registrarse a título informativo, pero esta versión no define verosimilitud para ellos: no alteran por sí solos la actualización.

## Resultado final

La salida final debe incluir, según el tipo de recurso:

- diagnóstico o nivel estimado;
- grado de confianza;
- dificultades detectadas;
- fortalezas observadas;
- recomendación pedagógica;
- siguiente paso.

Si es un itinerario o actividad de aprendizaje, añade además:

- recorrido seguido;
- etapas superadas o no;
- ayudas usadas;
- áreas a reforzar.

No declares un dominio alto basándote en muy pocos intentos. Si el resultado hace afirmaciones por categoría o dimensión, exige una muestra mínima en esas categorías o dimensiones antes de presentarlas como firmes (con olvido activo, esa muestra se cuenta sobre la ventana reciente de la distribución, no sobre el total histórico; véase «Refuerzo continuo sin parada»). Si la estimación es global, la muestra mínima puede referirse al conjunto de la sesión; limita o marca como provisional la estimación cuando la evidencia sea escasa.

No devuelvas solo una nota o etiqueta.

Si dos hipótesis terminan con probabilidades próximas, muestra la distribución posterior completa (por ejemplo, un diagrama de barras), no solo la etiqueta ganadora.

En la vista del alumno, la recomendación pedagógica y el siguiente paso deben tener **más peso visual** que la etiqueta de nivel. Formula el resultado en términos de tarea («te conviene practicar X antes de Y»), no de rasgo («eres nivel básico»): la literatura sobre expectativas indica que la etiqueta de rasgo tiene más riesgo. La etiqueta de nivel con su probabilidad conviene reservarla para la vista docente.

Si el modelo diagnostica un error concreto (por ejemplo, «confunde masa con peso», con su probabilidad), comunícaselo al alumno como una **hipótesis a comprobar juntos**, no como una sentencia («comprobemos si…»), especialmente en primaria. La etiqueta de error con su probabilidad es apropiada para la vista docente.

## Revisión docente del contenido

La validación bajo el modelo no sustituye la revisión del contenido, que solo el docente puede hacer bien. Al entregar el recurso, genera una lista de comprobación breve en lenguaje docente, sin tecnicismos, centrada en lo que el docente puede validar mejor que el sistema:

- ¿Estos errores son errores reales de tu alumnado?
- ¿Hay alguna pregunta demasiado fácil o demasiado difícil para el curso?
- ¿Las respuestas correctas y las explicaciones son correctas?
- ¿Falta algún caso importante del tema?
- ¿El lenguaje es adecuado para la edad?

Preséntala en la conversación al entregar el recurso o en la vista docente, nunca en la del alumno. No pidas al docente que revise parámetros, priors ni probabilidades: si señala un problema con sus palabras, ajusta tú el banco o el modelo.

Si el banco se genera por plantillas, la revisión docente es **por plantilla**, no por ítem: basta revisar una vez la regla y una muestra de sus variantes. Dilo explícitamente al entregar, para que el docente no crea que está validando un banco cerrado.

## Restricciones de implementación

- La interfaz debe ser comprensible para alumnado y profesorado.
- Debe mostrar con claridad el progreso y la retroalimentación.
- Si usas fórmulas visibles, acompáñalas de interpretación legible.
- Evita depender de backend si no se ha pedido.
- Evita preguntas abiertas largas sin corrección automática fiable.
- Accesibilidad mínima por defecto, aunque el docente no la pida: contraste suficiente, navegación por teclado, no transmitir información solo mediante el color, texto redimensionable y sin límite de tiempo por defecto (salvo que el diseño lo requiera y se avise).
- Privacidad por defecto: no envíes los datos del alumno fuera del navegador. El recurso estático sin backend ya lo garantiza y es la opción preferente al tratar datos de menores. Si se pide persistencia de resultados, advierte sobre la protección de datos y prefiere la exportación local (por ejemplo, descargar un archivo) frente a subirlos a un servidor.
- Incluye en la interfaz del recurso, de forma visible pero discreta (por ejemplo, en el pie o en una vista «Acerca de»), un enlace a la metodología de origen: `Metodología: recursos adaptativos bayesianos` → https://jjdeharo.github.io/recursos-adaptativos/. No lo ocultes en comentarios de código ni en documentación externa: debe acompañar al recurso generado.

## Valores por defecto recomendados

Si el docente no especifica parámetros:

- `n = 3` hipótesis o niveles;
- discriminación efectiva objetivo `a_ef = 1.25`; calcula siempre `a = 1.25 / (1 - c_q)` por pregunta (con `c_q = 0` da `a = 1.25`; máximo `a = 2.5` en verdadero/falso);
- `p_min = 0.80`;
- mínimo de preguntas: entre `4` y `6`;
- mínimo de diagnóstico por categoría en práctica adaptativa: `2` intentos;
- máximo práctico: entre `10` y `20`, según el tipo de recurso;
- peso de la ganancia de información en la fase de refuerzo: `α = 0.65` (rango razonable `0.6`–`0.7`);
- olvido exponencial: memoria efectiva `M = 20` intentos de cada distribución, de donde `lambda_d = (1 - 1/M)^(1 / K_d)` (`lambda = 0.95` si la distribución se actualiza en cada respuesta) en práctica o refuerzo continuo; `lambda = 1` en diagnóstico de sesión corta;
- crédito parcial: pesos de subcriterios definidos por el diseño, sumando `1`;
- muestra mínima por categoría o dimensión antes de mostrar dominio alto: `2`–`4` intentos.

## Qué no debe hacer la IA

- No confundir una explicación teórica con una regla obligatoria de implementación.
- No usar la creencia global para promocionar etapas locales en itinerarios.
- No cerrar el recurso sin justificar la certeza alcanzada.
- No presentar como firme un resultado con incertidumbre alta.
- No limitar la salida a una puntuación desnuda.
- No tratar como binaria una respuesta que admite grados: usa crédito parcial.
- No declarar dominio alto con muestra insuficiente.

## Validación y fiabilidad

Estas comprobaciones aumentan la honestidad del diagnóstico sin requerir datos empíricos. Aplícalas cuando la finalidad sea diagnóstica o el resultado vaya a usarse para decidir. La validación del diseño debe quedar preparada aunque la IA trabaje en un chat sin capacidad de ejecución.

- **Ajuste del patrón individual (person-fit).** Al cerrar una sesión, evalúa si el patrón de respuestas es coherente con el nivel estimado. Calcula el índice estandarizado `l_z` a partir de las probabilidades de acierto que el modelo asigna a las preguntas respondidas bajo la hipótesis más probable. Si `l_z` es muy negativo (orientativamente `< -2`), marca el diagnóstico como poco fiable aunque el posterior sea alto: suele indicar respuestas incoherentes con la dificultad, descuidos o azar. Es señal de cautela, no prueba formal; con pocas preguntas es solo orientativo.
- **Detección de azar o ansiedad durante la sesión (no solo al cierre).** No esperes al cierre para calcular el ajuste: si durante la sesión el person-fit o una racha inverosímil (fallar preguntas fáciles y acertar difíciles, o responder demasiado rápido) sugieren respuesta al azar o ansiedad, el recurso debería poder **pausar y reconducir** («parece que vas muy rápido, ¿seguimos con calma?») en lugar de seguir consumiendo banco. Hazlo con tacto, sin acusar, y reanuda con normalidad.
- **Verificación del banco generado.** Si los ítems se producen por plantillas, ejecuta antes de entregar la comprobación descrita en «Bancos generados» sobre unos cientos de variantes por plantilla, y trátala como condición de entrega, no como prueba opcional: mide la corrección del generador, no el dominio del alumno. Reporta cuántas variantes y cuántas plantillas se han comprobado. Si el entorno no permite ejecutar código, deja la utilidad escrita y marca el banco como «variantes pendientes de verificar»; no afirmes que están comprobadas.
- **Separabilidad del diseño (Monte Carlo).** Como propiedad del test (no del alumno), estima con qué fiabilidad el banco distingue los niveles: genera respondentes sintéticos situados en el `theta` de cada hipótesis, hazles el test reutilizando la misma selección adaptativa y el mismo criterio de parada, y construye la matriz de confusión (nivel real frente a diagnosticado). Preséntala como fiabilidad bajo el modelo, nunca como validez empírica: los respondentes salen del propio modelo, así que mide si el diseño discrimina los niveles, no si los parámetros reflejan la realidad. **Esta validación es una herramienta del creador del recurso, no del alumnado: no debe mostrarse en la interfaz del alumno.**
  - Si el entorno de la IA permite ejecutar código (CLI, entorno local, notebook), genera y ejecuta la simulación al construir el recurso.
  - Si la IA trabaja en chat sin ejecución, no afirmes que la validación está hecha: implementa una utilidad de validación en un archivo separado o en una vista docente/autora oculta al alumnado, con botón para ejecutarla en el navegador, y marca el diseño como «validación pendiente de ejecutar».
  - Usa por defecto al menos `500` simulaciones por hipótesis o perfil (`1000` si el navegador lo soporta con fluidez). Reporta matriz de confusión, exactitud equilibrada, tasa por hipótesis/perfil, tasa de resultados indeterminados y longitud media de la sesión.
  - Criterio orientativo: si alguna hipótesis relevante queda por debajo de `0.70` de clasificación correcta bajo el propio modelo, o si dos hipótesis se confunden de forma sistemática, no presentes el banco como bien separado; añade más ítems, revisa dificultades/verosimilitudes o declara explícitamente la limitación.

Consulta `matematicas.html §11.7–§11.8` (https://jjdeharo.github.io/recursos-adaptativos/matematicas.html#s11) para las fórmulas y el encuadre completo.

## Verificación antes de entregar

Comprueba el recurso generado contra esta lista. Los bloques condicionales, solo si corresponden al perfil y modo declarados en «Perfil y modo».

**Siempre:**

- Cada respuesta actualiza el posterior (verosimilitud × prior, normalizado); no hay reglas ad hoc de subir/bajar dificultad en su lugar.
- Ninguna respuesta aislada elimina una hipótesis ni fija un nivel máximo irreversible. Comprueba que, tras fallar la primera pregunta fácil y acertar después varias preguntas de dificultad media y alta, el nivel superior sigue siendo alcanzable.
- `a` derivada por ítem (`a = 1.25 / (1 - c_q)`) y techo de dominio `P(acierto) <= 0.95` aplicados en la verosimilitud.
- Escala `theta` fija según `n` (si el perfil usa `theta`), con las dificultades dentro de la mitad central.
- El resultado no es solo una nota: la recomendación y el siguiente paso pesan visualmente más que la etiqueta, y los errores se comunican como hipótesis a comprobar.
- Lista de comprobación docente generada (sobre contenido, no sobre parámetros).
- Si el banco se genera por plantillas: respuesta derivada de la regla (no transcrita), metadatos del modelo fijos por plantilla, verificación automática de las variantes ejecutada y una muestra leída a ojo.
- Accesibilidad mínima y privacidad por defecto (ningún dato del alumno sale del navegador).
- Enlace visible o accesible desde la interfaz a la metodología de origen: https://jjdeharo.github.io/recursos-adaptativos/.

**Si el perfil es `C` o `A+C`:**

- Prior de error `0.2`–`0.3`, no uniforme; `0.40` si el docente describe el error como frecuente, `0.10`–`0.15` si lo describe como raro (nunca `≥ 0.5` ni `< 0.10`).
- Ningún factor declarado presente o ausente sin su muestra mínima de evidencia; el reporte distingue «ausente confirmado» de «sin evidencia suficiente».
- Parada evaluada por factor; los no decididos se reportan como indeterminados, no se fuerzan.
- En `A+C`: selección por bloques pedagógicos con pesos según la finalidad; la parada por ganancia mínima se evalúa sobre la IG cruda, no sobre la utilidad normalizada.

**Si el modo es `Práctica`:**

- Olvido anclado al prior, con `lambda_d` por distribución según su frecuencia de actualización.
- Muestra mínima contada en ventana reciente; el contador visible para el alumno es el total real.
- Distribución sin evidencia reciente → «sin datos», nunca rojo.
- Un ítem cuya corrección ya se mostró no vuelve como evidencia plena: variantes parametrizadas o crédito parcial reducido, nunca exclusión de la actualización (con banco finito, la exclusión congela la estimación y bloquea la selección).
- Cada categoría cubre el rango de dificultades por sí sola: ninguna deja `ajuste = 0` para un nivel entero de alumnado.

**Si el modo es `Itinerario`:**

- Promoción con evidencia local de la etapa, más ítems de salida (sin verdadero/falso) o consistencia con el modelo; nunca un umbral fijo de porcentaje de aciertos bajo selección por máxima IG.
- Al repetir una etapa: estimación local reiniciada y ejercicios regenerados como variantes.

**Si la finalidad es diagnóstica:**

- Utilidad de validación Monte Carlo aparte (o en vista docente), sembrada y reproducible, con exactitud equilibrada, tasa de indeterminados, longitud media y alerta por debajo de `0.70`.
- Si no se pudo ejecutar, queda marcada como «validación pendiente de ejecutar», sin afirmar que el banco está comprobado.

## Nota sobre el modelo

La función IRT 3PL descrita aquí se usa como generador inicial de verosimilitudes cuando no hay datos empíricos. No equivale a una calibración psicométrica validada. Si se acumulan suficientes respuestas reales, conviene recalibrar dificultades, discriminación y pseudoazar.
