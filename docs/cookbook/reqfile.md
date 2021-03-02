# Cookbook - Directory & File Skeleton

## Install pipreqs
`pip install pipreqs`

## Generating a requirements file
After you're done writing the first iteration of a crawler,

1. Fetch the latest internal `sg*` libraries you'll use.
`pip install --upgrade sglogging` etc. for each library.
2. Run `pip freeze` and copy the output to the local `requirements.txt`
3. Run `pipreqs --clean requirements.txt`