import $exec.migrate_crawler_utils
import scala.util.matching._

lazy val allScrapersWithSgZip = all_scrapers filter {s => 
                                    requirements_txt_in_dir(s) map { req => File(req.toString).contentAsString.contains("sgzip") } getOrElse false
}

//println(allScrapersWithSgZip.toList.length) -> 446

lazy val allSgZipScripts = allScrapersWithSgZip flatMap all_python_scripts_in_dir filter { s => File(s.toString).contentAsString.contains("sgzip") }

//println(allScripts toList)

val activeNextCoord = """(?<!#[^\n]{0,20})next_coord""".r
val activeNextZip = """(?<!#[^\n]{0,20})next_zip""".r


lazy val zipSearchScriptsAll = allSgZipScripts filter (is_in_file(_, activeNextZip)) toSet
lazy val geoSearchScriptsAll = allSgZipScripts filter (is_in_file(_, activeNextCoord)) toSet

lazy val oddScripts = allSgZipScripts.toSet.filter(zipSearchScriptsAll).filter(geoSearchScriptsAll)

lazy val zipSearchScripts = zipSearchScriptsAll filterNot oddScripts.contains
lazy val geoSearchScripts = geoSearchScriptsAll filterNot oddScripts.contains

println(">> SKIPPING: Scrapers containing both next_zip() and next_coord() >>")
oddScripts foreach println
print(">> SANITY CHECK... >>")
assert((zipSearchScripts intersect geoSearchScripts).isEmpty)
println(" PASSED!")

def captureThineArguments(funcName: String): Regex = 
    s""".${funcName} *\(([^)]*)\)"""r


val initializeRgx = captureThineArguments("initialize")
val maxCountUpdateRgx = captureThineArguments("max_count_update")
val maxDistanceUptateRgx = captureThineArguments("max_distance_update")

sealed trait SearchType { val name: String }
case object DynamicZipSearch extends SearchType { val name = "DynamicZipSearch" }
case object DynamicGeoSearch extends SearchType { val name = "DynamicGeoSearch" }

sealed trait InitArgs
case class CountryCodes(value: List[String]) extends InitArgs
case class MaxCount(value: Int) extends InitArgs
case class MaxDistance(value: Double) extends InitArgs

def extractCountryCodes(rawArg: String): CountryCodes =
    CountryCodes(delete_all_from(rawArg, Seq("list\\(","\\)","\\[","\\]")).split(",").toList)


def captureInitArgs(fileText: String): List[InitArgs] = {
    val initArgs = initializeRgx.findFirstMatchIn(fileText).get.group(1)
    val splitInitArgs = initArgs.split(",")
    val parsedArgs = splitInitArgs.filter(_.nonEmpty).zipWithIndex.map { case (fatArg, idx) =>
        val thinArg = fatArg.replaceAll(" ", "")
        val nameValue = thinArg.split("=").map(_.trim())

        // index-based
        if (nameValue.size == 1) {
            idx match {
                case 0 => CountryCodes(List("CA"))
                case 1 => extractCountryCodes(nameValue.head)
            }
        } 
        // named arg
        else {
            (nameValue.head, nameValue.last) match {
                case ("include_canadian_fsas", value) => CountryCodes(List("CA"))
                case ("country_codes", value)         => extractCountryCodes(value)
            }
        }
    }

    val max_distance = fileText.findFirstMatchIn()

}

def subText(fileText: String, search: SearchType): String = {
    // 1. Replace with the proper class name 
    val text1 = fileText.replaceAll("ClosestNSearch", search.name)

    // 2. Capture initialization args
    val args = captureInitArgs(text1)
    val argStr = args.map()

    // 3. Transpose initialize args into zip search 
    val text2 = text1.replaceAll(captureThineArguments("initialize").toString, ".initialize()")
    val text3 = text2.replaceAll(s"${search.name}\\(\\)", )

}

val testScript = zipSearchScripts.head
//println(s"Test script ${testScript}")
//subText(File(testScript.toString).contentAsString)



zipSearchScripts foreach { scraper: os.Path =>
    val file = File(scraper.toString)
    println(s"File: ${scraper}")
    val newText = subText(file.contentAsString)

    // println(s"> ZIP: ${file}")

    // file.overwrite(newText)
}