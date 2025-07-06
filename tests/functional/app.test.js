const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Test configuration
const APP_URL = 'http://localhost:5003';
const SCREENSHOT_DIR = path.join(__dirname, '../../screenshots');

// Create screenshots directory if it doesn't exist
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

describe('Network Automation AI Agent Functional Tests', () => {
  let browser;
  let page;

  // Setup before tests
  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: 'new', // Use the new headless mode
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    page = await browser.newPage();
    // Set viewport size
    await page.setViewport({ width: 1280, height: 800 });
  });

  // Teardown after tests
  afterAll(async () => {
    await browser.close();
  });

  // Test the dashboard page
  test('Dashboard page loads correctly', async () => {
    await page.goto(`${APP_URL}/`, { waitUntil: 'networkidle0' });
    
    // Take a screenshot of the dashboard
    await page.screenshot({ 
      path: path.join(SCREENSHOT_DIR, 'dashboard.png'),
      fullPage: true 
    });
    
    // Check if the page title contains expected text
    const title = await page.title();
    expect(title).toContain('Network Automation');
    
    // Check if key elements exist
    const dashboardHeader = await page.$('h1');
    expect(dashboardHeader).not.toBeNull();
    
    // Check for navigation menu
    const navMenu = await page.$('nav');
    expect(navMenu).not.toBeNull();
  }, 30000); // Timeout of 30 seconds

  // Test the chat page
  test('Chat page loads correctly', async () => {
    await page.goto(`${APP_URL}/chat`, { waitUntil: 'networkidle0' });
    
    // Take a screenshot of the chat page
    await page.screenshot({ 
      path: path.join(SCREENSHOT_DIR, 'chat.png'),
      fullPage: true 
    });
    
    // Check for chat interface elements
    const chatContainer = await page.$('.chat-container');
    expect(chatContainer).not.toBeNull();
    
    // Check for message input field
    const messageInput = await page.$('textarea, input[type="text"]');
    expect(messageInput).not.toBeNull();
  }, 30000); // Timeout of 30 seconds

  // Test the devices page
  test('Devices page loads correctly', async () => {
    await page.goto(`${APP_URL}/devices`, { waitUntil: 'networkidle0' });
    
    // Take a screenshot of the devices page
    await page.screenshot({ 
      path: path.join(SCREENSHOT_DIR, 'devices.png'),
      fullPage: true 
    });
    
    // Check for devices list or table
    const devicesContainer = await page.$('.devices-container, table');
    expect(devicesContainer).not.toBeNull();
  }, 30000); // Timeout of 30 seconds

  // Test the documents page
  test('Documents page loads correctly', async () => {
    await page.goto(`${APP_URL}/documents`, { waitUntil: 'networkidle0' });
    
    // Take a screenshot of the documents page
    await page.screenshot({ 
      path: path.join(SCREENSHOT_DIR, 'documents.png'),
      fullPage: true 
    });
    
    // Check for documents list
    const documentsContainer = await page.$('.documents-container, table');
    expect(documentsContainer).not.toBeNull();
  }, 30000); // Timeout of 30 seconds
});
