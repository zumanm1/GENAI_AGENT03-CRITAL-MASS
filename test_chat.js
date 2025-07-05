const puppeteer = require('puppeteer');
const assert = require('assert');

(async () => {
    let browser;
    try {
        console.log('Launching browser...');
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();
        const testUrl = 'http://127.0.0.1:5003/chat';
        console.log(`Navigating to ${testUrl}...`);
        await page.goto(testUrl, { waitUntil: 'networkidle2' });

        // 1. Send a unique message
        const uniqueMessage = `Test message at ${new Date().toISOString()}`;
        const uniqueMessageLower = uniqueMessage.toLowerCase();
        console.log(`Typing message: "${uniqueMessage}"`);
        await page.type('#message-input', uniqueMessage);
        await page.click('#send-button');
        
        // Wait for the AI response to ensure the message is saved
        await page.waitForSelector('.ai-message', { timeout: 15000 });
        console.log('AI response received.');

        // 2. Reload the page
        console.log('Reloading the page...');
        await page.reload({ waitUntil: 'networkidle2' });
        
        // 3. Verify the message is in the history
        console.log('Verifying chat history...');
        await new Promise(r => setTimeout(r, 3000));
        const pageContent = await page.content();
        
        assert(pageContent.toLowerCase().includes(uniqueMessageLower), `FAILURE: The unique message was not found in the chat history.`);
        
        console.log('SUCCESS: Chat history test passed!');

    } catch (error) {
        console.error('ERROR: Chat history test failed.', error);
        process.exit(1); // Exit with error code
    } finally {
        if (browser) {
            await browser.close();
            console.log('Browser closed.');
        }
    }
})(); 