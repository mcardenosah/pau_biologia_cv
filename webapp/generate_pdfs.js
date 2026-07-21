import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';
import MarkdownIt from 'markdown-it';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const md = new MarkdownIt({ breaks: true });
const dataPath = path.join(__dirname, 'src', 'master_data.json');
const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));

// Diccionario para ayudar a ordenar meses
const monthOrder = { "Junio": 1, "Juny": 1, "Julio": 2, "Juliol": 2, "Septiembre": 3, "Setembre": 3 };

// Ordenar datos: de más antiguas a más nuevas
data.sort((a, b) => {
    if (a.year !== b.year) return a.year.localeCompare(b.year);
    const m1 = monthOrder[a.month] || 0;
    const m2 = monthOrder[b.month] || 0;
    if (m1 !== m2) return m1 - m2;
    return (a.option || '').localeCompare(b.option || '');
});

import http from 'http';

// Helper para convertir ruta de imagen a URL de localhost
function getImgSrc(imgRelPath) {
    if (!imgRelPath) return '';
    return 'http://localhost:9998/' + imgRelPath.replace(/^\//, '');
}

const css = `
<style>
    body { font-family: "Georgia", serif; font-size: 11pt; line-height: 1.5; margin: 0; color: #333; }
    h1 { font-family: "Arial", sans-serif; text-align: center; margin-top: 0; padding-bottom: 10px; border-bottom: 2px solid #ccc; page-break-before: always; }
    .question-card { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; page-break-inside: avoid; }
    .header-badge { font-family: "Arial", sans-serif; font-size: 0.9em; font-weight: bold; background: #eee; padding: 6px 10px; border-radius: 4px; display: inline-block; margin-bottom: 15px; }
    .image-container { text-align: center; margin: 15px 0; }
    .image-container img { max-width: 100%; max-height: 350px; border: 1px solid #ccc; border-radius: 4px; }
    .criteria { background: #f4fcf6; border-left: 4px solid #28a745; padding: 10px 15px; margin-top: 15px; font-size: 0.95em; }
    .criteria-title { font-family: "Arial", sans-serif; font-weight: bold; color: #1e7e34; margin-bottom: 5px; }
    
    /* Evitar el salto de página antes del primer H1 */
    body > h1:first-child { page-break-before: auto; }
</style>
`;

function buildHtml(questions, groupByFunc, groupTitleFunc) {
    let html = `<!DOCTYPE html><html><head><meta charset="utf-8">${css}</head><body>`;
    
    // Agrupar
    const groups = {};
    for (const q of questions) {
        const key = groupByFunc(q);
        if (!groups[key]) groups[key] = [];
        groups[key].push(q);
    }

    for (const [key, qList] of Object.entries(groups)) {
        html += `<h1>${groupTitleFunc(key)}</h1>`;
        for (const q of qList) {
            html += `<div class="question-card">`;
            html += `<div class="header-badge">Bloque ${q.block.split('-')[0]} | ${q.year} ${q.month} ${q.option ? `| Opción ${q.option}` : ''}</div>`;
            if (q.image) {
                html += `<div class="image-container"><img src="${getImgSrc(q.image)}" /></div>`;
            }
            html += `<div>${md.render(q.question || '*(Pregunta no disponible)*')}</div>`;
            if (q.criteria) {
                html += `<div class="criteria"><div class="criteria-title">Criterios de Corrección</div>${md.render(q.criteria)}</div>`;
            }
            html += `</div>`;
        }
    }
    html += `</body></html>`;
    return html;
}

// 1. Cronológico: Agrupar por Año
const htmlCronologico = buildHtml(data, q => q.year, key => `Año ${key}`);

// 2. Temático: Agrupar por Bloque
// Re-ordenar primero por bloque, luego por cronología
const dataBloques = [...data].sort((a, b) => {
    if (a.block !== b.block) return a.block.localeCompare(b.block);
    if (a.year !== b.year) return a.year.localeCompare(b.year);
    const m1 = monthOrder[a.month] || 0;
    const m2 = monthOrder[b.month] || 0;
    if (m1 !== m2) return m1 - m2;
    return (a.option || '').localeCompare(b.option || '');
});
const htmlTematico = buildHtml(dataBloques, q => q.block, key => `Bloque ${key}`);

// Servidor estático local para servir las imágenes a Puppeteer
const server = http.createServer((req, res) => {
    const filePath = path.join(__dirname, 'public', decodeURIComponent(req.url.split('?')[0]));
    if (fs.existsSync(filePath)) {
        res.writeHead(200);
        res.end(fs.readFileSync(filePath));
    } else {
        res.writeHead(404);
        res.end();
    }
});

(async () => {
    console.log("Iniciando servidor local de imágenes...");
    server.listen(9998);

    console.log("Iniciando Puppeteer...");
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    console.log("Generando PDF Cronológico...");
    await page.setContent(htmlCronologico, { waitUntil: 'networkidle0', timeout: 0 });
    await page.pdf({ 
        path: '../PAU_Biologia_Cronologico.pdf', 
        format: 'A4', 
        printBackground: true,
        timeout: 0,
        margin: { top: '20px', right: '20px', bottom: '20px', left: '20px' } 
    });

    console.log("Generando PDF Temático...");
    await page.setContent(htmlTematico, { waitUntil: 'networkidle0', timeout: 0 });
    await page.pdf({ 
        path: '../PAU_Biologia_Tematico.pdf', 
        format: 'A4', 
        printBackground: true,
        timeout: 0,
        margin: { top: '20px', right: '20px', bottom: '20px', left: '20px' } 
    });

    await browser.close();
    server.close();
    console.log("✅ PDFs generados con éxito: PAU_Biologia_Cronologico.pdf y PAU_Biologia_Tematico.pdf");
})();
