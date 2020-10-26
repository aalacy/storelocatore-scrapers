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

def insert_import(python_file: os.Path, import_line: String): Unit =
    insert_this_after(python_file, s"\n${import_line}\n", "import")

lazy val sg_dir = pwd / up

lazy val all_scrapers = all_authors(sg_dir) flatMap all_scrapers_from_author
