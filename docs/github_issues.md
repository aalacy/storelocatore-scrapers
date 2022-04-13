# Submitting GitHub Issues

## What it IS for:

- Bugs in our libraries.
- Bugs in our execution system (e.g.: no file attached after Jira run, went into a bad state in Jira, GitHub CI failed for an unexpected reason, etc.)
- Feature requests.

## What it ISN'T for:

- General communication
- Unsure if it's a bug (possible usage question)
- Questions (this channel is for them!)

## How To:

1. Go to [GitHub Issues](https://github.com/SafeGraphCrawl/crawl-service/issues)
2. Create a new issue
3. Give it a descriptive title
4. Fill in relevant details (including links to PR, Jira ticket, and code-snippets)
5. Choose proper labels:
   1. `blocking`- if you can't proceed with your work because of it
   2. `bug - if it's a bug
   3. `enhancement - if it's a feature request
   4. `sg library` - if it's a library issue, AND tag it with the library in question:
      1. `sgzip`
      2. `sgrequests`
      3. `sgselenium`
      4. `sgscrape`
6. Link to the issue in the `#sg-crawlers-external` Slack channel, possibly tagging the proper person to deal with it (e.g. @Victor Ivri (Eng) for library bugs, or @Mia for )
