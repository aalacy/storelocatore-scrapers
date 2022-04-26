# Crawl Cookbook

> The canonical source of best practices in writing crawlers/scrapers

## Table of Contents

### Templates

- [Experimental Live Realtime Templating Engine](./cookbook/crawly_web.md)
- [Template types and uses](./cookbook/templates.md)

### Basics

- [Git Workflow](./cookbook/git_workflow.md)
- [Directory & File Skeleton](./cookbook/dir_skeleton.md)
- [Generating a Python requirements file](./cookbook/reqfile.md)
- [External Logging documentation](https://docs.google.com/document/d/1I-1Atok4pd1RKW_ZfRzv7rMnuYTV0R_yo8QMnCSdwdE/view).

### Records and Identity

- [Understanding What a Record Means](./cookbook/records_and_id.md)

### Writing to `data.csv`

- [Using SgWriter](./cookbook/sgwriter.md)

### Search for Locations Using Zipcodes / Coordinates

- [Our sgzip documentation.](./cookbook/sgzip.md)
- [Parallel sgzip traversal](./cookbook/sgzip-par.md)

### Long-Running Crawls

- [Using CrawlState to write long-running crawls](./cookbook/pause_resume.md)

### Parsing Raw Addresses

- [Using sgpostal](./cookbook/sgpostal.md)

### Declarative Pipeline / SimpleScraperPipeline

- [Using the Declarative Field Mapping](./cookbook/declarative_pipeline.md)

### Fetching data

- [Request anything over HTTP with SgRequests](./cookbook/sgrequests.md)
- [TODO] Parse JSON results
- [TODO] Parse XML results
- [TODO] Parse HTML results
- [TODO] Traverse paginated content
- [TODO] Requests that are very slow
