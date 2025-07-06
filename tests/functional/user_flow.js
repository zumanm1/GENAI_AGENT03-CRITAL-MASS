const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  const APP_URL = 'http://localhost:5003';
  const SCREENSHOT_DIR = path.join(__dirname, '../../screenshots');
  if (!fs.existsSync(SCREENSHOT_DIR)) fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  console.log('Opening dashboard');
  await page.goto(`${APP_URL}/`, { waitUntil: 'networkidle0' });
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'flow_dashboard.png') });

  console.log('Navigating to chat');
  await page.goto(`${APP_URL}/chat`, { waitUntil: 'networkidle0' });
  await page.waitForSelector('#message-input');
  await page.type('#message-input', 'Hello AI assistant!');
  await page.click('#send-button');
  // wait for assistant response
  await page.waitForFunction(() => {
    const msgs = document.querySelectorAll('.assistant-message');
    return msgs.length > 1; // initial greeting plus response
  }, { timeout: 15000 });
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'flow_chat.png') });

  console.log('Navigating to devices');
  await page.goto(`${APP_URL}/devices`, { waitUntil: 'networkidle0' });
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'flow_devices.png') });

  console.log('Navigating to documents');
  await page.goto(`${APP_URL}/documents`, { waitUntil: 'networkidle0' });
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'flow_documents.png') });

  await browser.close();
  console.log('User flow completed. Screenshots saved to', SCREENSHOT_DIR);
})();
