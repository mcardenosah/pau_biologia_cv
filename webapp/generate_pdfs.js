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
    return 'http://localhost:9997/' + imgRelPath.replace(/^\//, '');
}

const css = `
body { font-family: "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 20px; font-size: 14px; color: #333; }
.question { margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #eee; break-inside: avoid; }
.header { font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #1a5f7a; }
.text { margin-bottom: 15px; line-height: 1.5; white-space: pre-wrap; }
.criteria { background-color: #f8f9fa; padding: 15px; border-left: 4px solid #1a5f7a; margin-top: 10px; font-size: 13px; white-space: pre-wrap; }
.image { max-width: 100%; height: auto; max-height: 400px; margin: 15px 0; border: 1px solid #ddd; }
.block-title { font-size: 24px; color: #000; border-bottom: 2px solid #1a5f7a; padding-bottom: 5px; margin-top: 40px; margin-bottom: 20px; break-before: page; }
.page-break { page-break-after: always; }
`;

function buildHtml(dataList, groupByFunc, groupTitleFunc) {
    let html = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${css}</style></head><body>`;
    
    const groups = new Map();
    for (const q of dataList) {
        const key = groupByFunc(q);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(q);
    }

    for (const [key, qs] of groups.entries()) {
        html += `<div class="block-title">${groupTitleFunc(key)}</div>`;
        for (const q of qs) {
            html += `<div class="question">`;
            html += `<div class="header">${q.year} - ${q.month} - Opción ${q.option}</div>`;
            html += `<div class="text"><strong>Pregunta:</strong>\n${q.question}</div>`;
            if (q.image) {
                const src = getImgSrc(q.image);
                if (src) html += `<img class="image" src="${src}" />`;
            }
            if (q.criteria) {
                html += `<div class="criteria"><strong>Criterios de corrección:</strong>\n${q.criteria}</div>`;
            }
            html += `</div>`;
        }
    }
    
    html += `</body></html>`;
    return html;
}

const dataCronologico = [...data].sort((a, b) => b.year - a.year || a.month.localeCompare(b.month) || (a.option || '').localeCompare(b.option || ''));
const htmlCronologico = buildHtml(dataCronologico, q => q.year, key => `Exámenes ${key}`);

const dataBloques = [...data].sort((a, b) => {
    const bA = (a.block || '').toString();
    const bB = (b.block || '').toString();
    if (bA !== bB) return bA.localeCompare(bB);
    if (b.year !== a.year) return b.year - a.year;
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
    server.listen(9997);

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
