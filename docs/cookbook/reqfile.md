# Cookbook - Requirement File Generation

## Installation
* Official [documentation and setup instructions](https://docs.python.org/3/library/venv.html).
* A Windows 10 [installation guide](https://www.liquidweb.com/kb/how-to-setup-a-python-virtual-environment-on-windows-10/).

## In Use
* Your `requirements.txt` file should include _all_ the dependencies the crawler will require, together with their exact 
versions.

**An easy way to do that, is via a virtual environment:**
1. Navigate to the new crawl folder.
1. Execute `python3 -m venv cw_venv` to create a local virtual environment.
      * It will complain if it's not installed yet, please follow the
1. Execute `source cw_venv/bin/activate` in the `bash` shell, or `cw_venv/bin/Activate.ps1` in `PowerShell` to activate the 
   virtual environment.
1. Run `pip install sgcrawler` to get the latest supported versions of most libraries.
1. Run `pip freeze`, and paste the output to `requirements.txt`. In bash: `pip freeze > requirements.txt`
   * Make sure to exclude (delete) anything that has a `git` path in the `requirements.txt` file.
1. Run `deactivate` to deactivate the virtual environment at the end of a development session.   

**When done active development**
1. To destroy the virtual environment files, and free up space, delete the local `cw_venv` folder.