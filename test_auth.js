const puppeteer = require('puppeteer');
const assert = require('assert');

(async () => {
    let browser;
    let page;
    try {
        console.log('Launching browser for auth test...');
        browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
        page = await browser.newPage();
        const baseUrl = 'http://127.0.0.1:5003';

        // Generate unique credentials
        const ts = Date.now();
        const username = `user_${ts}`;
        const email = `user_${ts}@example.com`;
        const password = 'testpassword';

        // 1) Visit registration page and register
        console.log('Navigating to /register ...');
        await page.goto(`${baseUrl}/register`, { waitUntil: 'domcontentloaded' });
        await page.waitForSelector('form[action="/register"]');

        await page.type('input[name="username"]', username);
        await page.type('input[name="email"]', email);
        await page.type('input[name="password"]', password);
        await page.click('button[type="submit"]');
        await page.waitForNavigation({ waitUntil: 'domcontentloaded' });

        // After registration we should land on /login
        assert(page.url().includes('/login'), 'Registration did not redirect to login page');
        console.log('Registration successful and redirected to login.');

        // 2) Login with the new credentials
        console.log('Logging in...');
        await page.waitForSelector('form[action="/login"]');
        await page.type('input[name="username"]', username);
        await page.type('input[name="password"]', password);
        await page.click('button[type="submit"]');
        await page.waitForNavigation({ waitUntil: 'domcontentloaded' });

        // After login we should land on /dashboard
        assert(page.url().includes('/dashboard'), 'Login did not redirect to dashboard page');
        console.log('Login successful and redirected to dashboard.');

        // 3) Logout
        console.log('Logging out...');
        await page.waitForSelector('a[href="/logout"]');
        await page.click('a[href="/logout"]');
        await page.waitForNavigation({ waitUntil: 'domcontentloaded' });

        // 4) Verify logout by checking for the login form
        await page.waitForSelector('form[action="/login"]');
        assert(page.url().includes('/login'), 'Logout did not redirect to login');
        console.log('Logout successful.');

        console.log('SUCCESS: Auth flow test passed!');
    } catch (err) {
        console.error('ERROR: Auth flow test failed.', err);
        const pageContent = await page.content();
        console.log('Page content at time of error:', pageContent);
        process.exit(1);
    } finally {
        if (browser) {
            await browser.close();
            console.log('Browser closed.');
        }
    }
})(); 