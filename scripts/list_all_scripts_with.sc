import $exec.`migrate_crawler_utils`

@main
def all() = all_with_regex("")


@main
def with_regex(scriptPath: String, searchForRe: String = ".info\\(\\)") = {
    if (is_in_file(Path(scriptPath), searchForRe.r))
        println (scriptPath)
}

@main
def all_with_regex(searchForRe: String) = {
    val all_python_scripts = all_scrapers flatMap all_python_scripts_in_dir
    all_python_scripts foreach (s => with_regex(s.toString, searchForRe))
}
