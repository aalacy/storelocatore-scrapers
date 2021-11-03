# Cookbook - Git Workflow
__This document covers using the Git CLI.__ 

>__If you're using some other visual software, try to follow as closely as possible.__


## Happy-Path
### Starting to work on a Jira ticket
1. Get the latest master
   ```bash
   git checkout master 
   git pull
   ``` 
1. Create the branch _on top of latest master_
   ```bash
   git checkout -b SLC-<Jira ticket number> # e.g. SLC-1234
   ```
1. Doing work on the branch _only in your crawler directory_

1. Committing your work:
   ```bash
   cd <your crawler directory>
   git add .
   git commit -m "SCL-<Jira ticket number>: <your directory name> <optional msg>" # e.g. "SLC-1234: vivri/store_com"
   ```
1. Pushing your branch to GitHub
   ```bash
   git fetch
   git merge origin/master
   git push origin HEAD
   ```

## Troubleshooting
1. __`git checkout master` isn't working__
   * That usually means you have some unstaged changes.
      * Either commit your changes in the current (or new branch).
      * Save them for later using [git stash](https://git-scm.com/docs/git-stash)
      * Discard them completely using `git reset --hard`

1. __`git merge origin/master` says there are conflicts__
   * _Oh noes!_
   * [Here are docs](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/resolving-a-merge-conflict-using-the-command-line) to resolve conflicts.
   * Remember to always `git add <files in conflict>` and `git commit` to mark resolved.
   
1. __Something Else__
   * Using the Git CLI isn't always a walk in the park!
   * But we're here for you.
   * If you haven't found the answer you were looking for, please ask in `#sg-crawlers-external`, and we might add the 
     solution to this document.
     