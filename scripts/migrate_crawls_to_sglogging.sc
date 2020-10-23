/**
  * This is a Scala Ammonite script: https://ammonite.io/
  * Run using `amm migrate_crawls_to_sglogging.sc` 
  * From the `scripts` directory to get the rel paths right.
  * 
  */

import ammonite.ops._
import $ivy.`com.github.pathikrit::better-files:3.9.1`
import better.files._
import File._
import java.io.{File => JFile}
import scala.util.Try

def all_authors(sgBasePath: os.Path): Stream[os.Path] = 
    ls(sgBasePath / 'apify).toStream.filter(_.isDir)

def maybePath (path: => os.Path): Option[os.Path] =
    Try { 
        ls(path)
        path
    } toOption

def all_scrapers_from_author(authorBasePath: os.Path): Stream[os.Path] = {
    val all_dirs = 
        List(maybePath(authorBasePath / 'storelocator), maybePath(authorBasePath / 'curatedsources))
            .foldLeft(List.empty[os.Path]) { (accum, next) =>
                accum ++ (next map { path => ls(path) } getOrElse Nil)
            }

    all_dirs.toStream.filter { dir =>
        if (dir.isDir) {
            val non_private = !dir.segments.toList.last.startsWith(".")
            val has_dockerfile = ls(dir).exists(_.segments.toList.last == "Dockerfile")
            non_private && has_dockerfile
        } else false
    }
}

def all_python_scripts_in_dir(dir: os.Path): Stream[os.Path] =
    ls(dir).toStream.filter(_.toString.endsWith(".py"))

def requirements_txt_in_dir(dir: os.Path): Option[os.Path] =
    ls(dir).filter(_.toString.contains("requirements.txt")).headOption

def is_sglogging_not_in_reqs(reqs_file: os.Path): Boolean = 
    !File(reqs_file.toString).contentAsString.contains("sglogging")

def insert_sglogging_in_reqs(reqs_file: os.Path): Unit = {
    val reqfile = File(reqs_file.toString)
    reqfile appendLine "sglogging"
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
    val has_prints = all_python_scripts_in_dir(scraper_dir) filter has_print_statements
    if (has_prints.nonEmpty) {
        requirements_txt_in_dir(scraper_dir) map insert_sglogging_in_reqs
        has_prints map { python_script =>
            insert_import(python_script)
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

lazy val test_dir = sg_dir / 'apify / 'himanshu / 'storelocator / 'lotsa_com

// Executes the program
full_program.toList

// println(all_scrapers.size, all_scrapers.toSet.size)

//process_scraper(test_dir) // TESTING
