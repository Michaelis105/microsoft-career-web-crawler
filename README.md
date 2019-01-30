# microsoft-career-web-crawler
Personal web crawler that retrieves Microsoft software engineering positions based on filters.

Use with care and please do not DDOS Microsoft.

## How to use
```
pip install beautifulsoup4
```

```
python microsoft_career_web_crawler.py
```
## Statistics

Crawler takes about 5 minutes to:
- Call Microsoft career endpoint to retrieve list of 1500 software engineering jobs
- Remove all job reqs that contain senior/specialized titles or not within entry-level SDE levels (59-62)
- Search each isolated job id description for keywords "invitation-only, interview day"

