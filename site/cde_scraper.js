#!/usr/bin/env node
// CDE 药审中心抓取 — 用 puppeteer-core + 系统 Chrome
const puppeteer = require('puppeteer-core');
const fs = require('fs');

const CDE_PAGES = [
  { url: 'https://www.cde.org.cn/main/news/listpage/545', label: '新闻中心' },
  { url: 'https://www.cde.org.cn/main/xxgk/listpage/9f9c74c73e0f8f56a8bfbc646055026d', label: '信息公开' },
];

const CDE_DAYS = 5;
const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d;
}

(async () => {
  const cutoff = daysAgo(CDE_DAYS);
  const results = [];
  const seen = new Set();

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });

  try {
    for (const pageInfo of CDE_PAGES) {
      const page = await browser.newPage();
      await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36');

      try {
        console.error(`[CDE] Loading ${pageInfo.label}...`);
        await page.goto(pageInfo.url, { waitUntil: 'networkidle2', timeout: 30000 });

        // Wait for content to load (JS-rendered)
        await page.waitForSelector('a[href*="viewInfoCommon"], a[href*="listpage"]', { timeout: 10000 }).catch(() => {});

        const content = await page.content();

        // Extract news links with dates
        const items = await page.evaluate(() => {
          const results = [];
          const links = document.querySelectorAll('a');

          links.forEach(a => {
            const href = a.getAttribute('href') || '';
            const text = a.textContent.trim();

            // Only match news detail pages
            if (!href.includes('viewInfoCommon') && !href.includes('/main/news/') &&
                !href.includes('/main/xxgk/')) return;
            if (text.length < 4 || text.length > 200) return;

            // Try to find date nearby (look at parent/ancestor for date pattern)
            let dateEl = a.closest('li,div.tr,tr,div.item');
            let dateStr = '';
            if (dateEl) {
              const dateMatch = dateEl.textContent.match(/(\d{4}[-/]\d{2}[-/]\d{2})/);
              if (dateMatch) dateStr = dateMatch[1];
            }

            results.push({ href, title: text, dateStr });
          });
          return results;
        });

        console.error(`[CDE] ${pageInfo.label}: found ${items.length} raw links`);

        for (const item of items) {
          if (item.dateStr) {
            const d = new Date(item.dateStr);
            if (d < cutoff) continue;
          }
          const key = item.href;
          if (seen.has(key)) continue;
          seen.add(key);

          let fullUrl = item.href;
          if (!fullUrl.startsWith('http')) {
            fullUrl = 'https://www.cde.org.cn' + (fullUrl.startsWith('/') ? '' : '/') + fullUrl;
          }

          results.push({
            title: item.title,
            url: fullUrl,
            source: 'CDE 药审中心',
            time: item.dateStr ? item.dateStr + 'T00:00:00Z' : new Date().toISOString().split('T')[0] + 'T00:00:00Z',
            desc: '',
            section: item.title.includes('指南') || item.title.includes('指导原则') || item.title.includes('征求意见')
              ? '政策追踪' : '监管审批',
          });
        }
      } catch (e) {
        console.error(`[CDE] ${pageInfo.label} error: ${e.message}`);
      } finally {
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }

  // Output as JSON
  console.log(JSON.stringify(results, null, 2));
  console.error(`[CDE] Total: ${results.length} items`);
})().catch(e => {
  console.error(`Fatal: ${e.message}`);
  process.exit(1);
});
