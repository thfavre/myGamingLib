# CAPTCHA Fix Update

The scraper has been updated to bypass CAPTCHA and bot detection using `undetected-chromedriver`.

## Apply the Fix

**Stop the app if it's running** (Ctrl+C in the terminal)

**Update dependencies** (this fixes the distutils error on Python 3.12+):
```bash
pip install --upgrade setuptools
pip install -r requirements.txt
```

**Restart the app**:
```bash
python app.py
```

**Try scraping again** - The browser should now bypass CAPTCHA automatically!

## What Changed

- Replaced regular Selenium ChromeDriver with `undetected-chromedriver`
- This library automatically patches Chrome to appear as a normal user browser
- Epic Games will no longer detect it as a bot
- CAPTCHA should not appear anymore

## If You Still See CAPTCHA

This is very rare with undetected-chromedriver, but if it happens:

1. Make sure you updated dependencies: `pip install undetected-chromedriver`
2. Close ALL Chrome windows before starting the scraper
3. Make sure Chrome is up-to-date
4. Try clearing Chrome's cache and cookies
5. Wait a few minutes before trying again (rate limiting)

## Note

The first time you run with undetected-chromedriver, it may take a bit longer to start as it patches the Chrome binary. This is normal.
