import $exec.migrate_crawler_utils

def is_sglogging_not_in_reqs(reqs_file: os.Path): Boolean = 
    !File(reqs_file.toString).contentAsString.contains("sglogging")

def insert_sglogging_in_reqs(reqs_file: os.Path): Unit = {
    val reqfile = File(reqs_file.toString)
    val old_string = reqfile.contentAsString
    val new_content = s"${old_string}\nsglogging\n".replaceAll("\n+", "\n")
    reqfile overwrite new_content
}

def has_print_statements(python_file_path: os.Path): Boolean =
    File(python_file_path.toString).contentAsString.indexOf("print") != -1

def replace_prints(python_file_path: os.Path): Unit = {
    val python_file = File(python_file_path.toString)

    val old_string = python_file.contentAsString

    python_file.overwrite(
        old_string.replaceAll("print\\(", "logger.info(")
                  .replaceAll("print \\(", "logger.info("))
}

def mk_logger(python_file_path: os.Path, dirname: String): Unit =
    insert_this_after(python_file_path, s"\n\nlogger = SgLogSetup().get_logger('${dirname}')\n", "import")

def process_scraper(scraper_dir: os.Path) {
    val has_prints = all_python_scripts_in_dir(scraper_dir) filter has_print_statements
    if (has_prints.nonEmpty) {
        requirements_txt_in_dir(scraper_dir) map insert_sglogging_in_reqs
        has_prints map { python_script =>
            insert_import(python_script, "from sglogging import SgLogSetup")
            mk_logger(python_script, scraper_dir.segments.toList.last)
            replace_prints(python_script)
        } 
    } else {
        println(s"Skipping scraper dir ${scraper_dir}")
    }
}

lazy val sg_dir = pwd / up

lazy val all_scrapers = all_authors(sg_dir) flatMap all_scrapers_from_author

lazy val scrapers_without_sglogging = all_scrapers.filter { scraper_dir =>
    (requirements_txt_in_dir(scraper_dir) map is_sglogging_not_in_reqs) getOrElse false
}

lazy val num_of_dirs = scrapers_without_sglogging.length

lazy val full_program = scrapers_without_sglogging.zipWithIndex map { case (dir, idx) => 
    println(s"[${idx} / ${num_of_dirs}] Processing $dir ...")
    process_scraper(dir)
}

lazy val aleenahs_scrapers = all_scrapers_from_author(sg_dir / 'apify / 'aleenah) filter { scraper_dir =>
    (requirements_txt_in_dir(scraper_dir) map is_sglogging_not_in_reqs) getOrElse false
}

lazy val migrate_aleenah = aleenahs_scrapers.zipWithIndex map { case (dir, idx) => 
    println(s"[${idx} / ${aleenahs_scrapers.length}] Processing $dir ...")
    process_scraper(dir)
}

// Migrate Aleenah's scrapers
migrate_aleenah.toList

// Executes the program
// full_program.toList

// println(all_scrapers.size, all_scrapers.toSet.size)

//process_scraper(test_dir) // TESTING
