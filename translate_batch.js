#!/usr/bin/env node
// 批量翻译：接收 JSON 文本数组，输出翻译后的 JSON 数组
const translate = require('@vitalets/google-translate-api');

const texts = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf-8'));

(async () => {
  const results = [];
  for (let i = 0; i < texts.length; i++) {
    const txt = texts[i];
    if (!txt || txt.length < 3) {
      results.push(txt);
      continue;
    }
    try {
      const res = await translate(txt, { from: 'auto', to: 'zh-CN' });
      results.push(res.text || txt);
    } catch (e) {
      results.push(txt);
    }
    if ((i + 1) % 10 === 0) {
      process.stderr.write(`  [${i+1}/${texts.length}]\n`);
    }
  }
  console.log(JSON.stringify(results));
})();
