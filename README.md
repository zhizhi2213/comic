# Manga Scraper - Comicbox

A Python web scraper that automatically downloads manga chapters from comicbox.xyz, designed to run daily via GitHub Actions.

## Features

- 📚 Automatically scrapes all chapters from a manga book
- ⏰ Scheduled daily updates via GitHub Actions
- 💾 Downloads images organized by chapter
- 🔄 Tracks progress to avoid re-downloading
- 🎨 High-quality image downloads

## Files Structure

```
manhua/
├── scraper.py              # Main scraper script
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── .github/
    └── workflows/
        └── daily_scraper.yml  # GitHub Actions workflow
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Locally

```bash
python scraper.py
```

### 3. Configure for Your Book

Edit `scraper.py` and change these lines:

```python
BOOK_URL = "https://www.comicbox.xyz/book/4638?id=4638"
BOOK_ID = "4638"
```

Replace with your desired book URL and ID.

## GitHub Actions Setup

### Enable Workflows

1. Go to your repository on GitHub
2. Click on "Actions" tab
3. Click "I understand my workflows, go ahead and enable them"

### Manual Trigger

You can manually trigger the scraper:

1. Go to Actions tab
2. Select "Daily Manga Scraper"
3. Click "Run workflow"
4. Optionally provide a different book URL
5. Click "Run workflow"

### Schedule Configuration

By default, it runs daily at 00:00 UTC. To change the schedule, edit `.github/workflows/daily_scraper.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Change this cron expression
```

Cron format: `minute hour day month weekday`

Examples:
- `0 12 * * *` - Daily at noon UTC
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1` - Every Monday at midnight

## Usage

The scraper will:
1. Create a `downloads/` directory
2. Download each chapter into separate folders
3. Save progress in `downloads/progress.json`
4. Organize images as: `downloads/chapter_001_Name/001.jpg, 002.jpg...`

## Output Structure

```
downloads/
├── chapter_001_Chapter_Title/
│   ├── 001.jpg
│   ├── 002.jpg
│   └── ...
├── chapter_002_Next_Chapter/
│   ├── 001.jpg
│   └── ...
└── progress.json
```

## Notes

- ⚠️ **Respect the website**: Add delays between requests to avoid overloading the server
- ⚠️ **Copyright**: Only download content you have rights to use
- ⚠️ **Terms of Service**: Check the website's terms before scraping
- The `downloads/` folder is in `.gitignore` if you don't want to commit files
- GitHub Actions will upload downloads as artifacts (retained for 30 days)

## Troubleshooting

### No images downloaded
- Website structure may have changed
- Check console output for errors
- May need to update image extraction logic in `extract_image_urls()` method

### GitHub Actions failing
- Check Actions logs for error details
- Ensure dependencies are correctly installed
- Verify the book URL is accessible

### Rate limiting
- If blocked, increase delay between requests in `scrape_chapter()` method
- Consider adding proxy rotation for large downloads

## Customization

### Change Download Location

Edit `download_dir` in `ComicboxScraper.__init__()`:

```python
self.download_dir = Path("custom/path")
```

### Adjust Request Delays

Modify sleep times in `scrape_chapter()`:

```python
time.sleep(1.0)  # Increase for slower downloads
```

## License

This tool is for educational purposes only. Respect copyright and website terms of service.
