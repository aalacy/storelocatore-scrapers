import $exec.`migrate_crawler_utils`

all_scrapers flatMap all_python_scripts_in_dir filter (x => is_in_file(x, "SgLog".r)) foreach println
