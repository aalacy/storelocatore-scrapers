import ammonite.ops._
import $ivy.`com.github.pathikrit::better-files:3.9.1`
import better.files._
import File._
import java.io.{File => JFile}

def all_authors(sgBasePath: os.Path): Stream[os.Path] = 
    ls(sgBasePath / 'apify).filter(_.isDir).toStream

def all_scrapers_from_author(authorBasePath: os.Path): Stream[os.Path] = {
    val all_dirs = ls(authorBasePath / 'storelocator) ++ ls(authorBasePath / 'storelocator)
    all_dirs.filter { dir =>
        if (dir.isDir) {
            val non_private = !dir.segments.toList.last.startsWith(".")
            val has_dockerfile = ls(dir).exists(_.segments.toList.last == "Dockerfile")
            non_private && has_dockerfile
        } else false
    }.toStream
}

def all_python_scripts_in_dir(dir: os.Path): Stream[os.Path] =
    ls(dir).filter(_.toString.endsWith(".py")).toStream

def requirements_txt_in_dir(dir: os.Path): Option[os.Path] =
    ls(dir).filter(_.toString.contains("requirements.txt")).headOption

def is_sglogging_not_in_reqs(reqs_file: os.Path): Boolean = 
    !File(reqs_file.toString).contentAsString.contains("sglogging")

def insert_sglogging_in_reqs(reqs_file: os.Path): Unit = {
    val reqfile = File(reqs_file.toString)
    reqfile appendLine "sglogging"
}

def replace_prints(python_file_path: os.Path): Unit = {
    val python_file = File(python_file_path.toString)

    val old_string = python_file.contentAsString

    python_file.overwrite(old_string.replaceAll("print\\(", "logger.info(").replaceAll("print \\(", "logger.info("))
}

def insert_this_after(file_path: os.Path, insert: String, after_last: String): Unit = {
    val file = File(file_path.toString)
    val old_text = file.contentAsString
    val last_import = old_text.lastIndexOf(after_last)
    if (last_import != -1) {
        val next_line_start = old_text.indexOf("\n", last_import)
        val part1 = old_text.substring(0, next_line_start)
        val part2 = old_text.substring(next_line_start, old_text.length())
        val new_text = part1 + insert + part2
        file.overwrite(new_text)
    }
}

def mk_logger(python_file_path: os.Path, dirname: String): Unit =
    insert_this_after(python_file_path, s"\n\nlogger = SgLogSetup().get_logger('${dirname}')\n", "import")
    
def insert_import(python_file: os.Path): Unit =
    insert_this_after(python_file, "\nfrom sglogging import SgLogSetup\n", "import")

def process_scraper(scraper_dir: os.Path) {
    requirements_txt_in_dir(scraper_dir) map insert_sglogging_in_reqs
    all_python_scripts_in_dir(scraper_dir) map { python_script =>
        insert_import(python_script)
        replace_prints(python_script)
        mk_logger(python_script, scraper_dir.segments.toList.last)
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

lazy val test_dir = sg_dir / 'apify / 'himanshu / 'storelocator / 'lotsa_com

full_program.toList

//process_scraper(test_dir) // TESTING
