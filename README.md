# AI News Agent

Get a daily AI news digest in your inbox, built with Python, the Gemini API and GitHub Actions.

## How it works
GitHub Actions (daily) -> fetch RSS news -> Gemini summarizes -> Gmail sends the email

## Setup
1. Fork or clone this repo.
2. Get a Gemini API key at aistudio.google.com/apikey.
3. Turn on 2-Step Verification on your Google account, then create an
   App Password at myaccount.google.com/apppasswords.
4. Run locally: copy `.env.example` to `.env`, fill in your values, then
   `pip install -r requirements.txt` and `python agent.py`.
5. Run daily: in your repo go to Settings -> Secrets and variables -> Actions
   and add `GEMINI_API_KEY`, `GMAIL_USER` and `GMAIL_APP_PASSWORD`.
6. Change the time in `.github/workflows/daily.yml`. Cron uses UTC.
   Example: `30 1 * * *` is 7:00 AM India time.

## Customize
- `FEEDS` in `agent.py`: add or remove news sources
- `LOOKBACK_HOURS`: 24 for daily, 168 for weekly
- `MODEL`: change it if Google retires the model name

## Notes
- Never commit your `.env` file.
- Scheduled GitHub Actions on public repos pause after 60 days of no repo
  activity. Re-enable them from the Actions tab.

## License
MIT