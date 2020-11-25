import $exec.migrate_crawler_utils
import scala.util.matching._
import java.util.concurrent.atomic.AtomicInteger

case class ExpectedException(reason: String) extends Exception(reason)

lazy val allScrapersWithSgZip = all_scrapers filter {s => 
                                    requirements_txt_in_dir(s) map { req => 
                                        File(req.toString).contentAsString.contains("sgzip")
                                    } getOrElse false
                                }

val floatingPointNum = """\d+(\.\d+)?"""

sealed trait PythonArg { val value: String }
case class PositionalArg(idx: Int, value: String) extends PythonArg
case class NamedArg(name: String, value: String) extends PythonArg

def captureArgs(rawArgs: String): List[PythonArg] = {

    case class NxtArgBuilderState(argInProgress: List[Char] = Nil,
                                  specialStack: List[Char] = Nil,
                                  nameOfArg: String = "")

    val specialStackCharBoundaries = Map(
        '(' -> ')',
        '[' -> ']',
        '"' -> '"',
        '\'' -> '\''
    )

    val specialStackCharStarters = specialStackCharBoundaries.keySet

    def toArg(argInProgressReversed: List[Char]): String = 
        argInProgressReversed.reverse.mkString.trim

    val EOL = '\u0000'

    val (argsReversed, _) = (rawArgs+EOL).foldLeft((List.empty[PythonArg], NxtArgBuilderState())) { case ((argsRev, bldr), char) =>
        bldr match {
            // step out of special sequence in stack
            case NxtArgBuilderState(partRev, x :: stack, nameOfArg) if specialStackCharBoundaries(x) == char =>
                (argsRev, NxtArgBuilderState(char :: partRev, stack, nameOfArg))
            
            // step into special sequence in stack
            case NxtArgBuilderState(partRev, specialStack, nameOfArg) if specialStackCharStarters.contains(char) =>
                (argsRev, NxtArgBuilderState(char :: partRev, char :: specialStack, nameOfArg))

            // remain in special sequence stack
            case NxtArgBuilderState(partRev, specialStack, nameOfArg) if specialStack.nonEmpty =>
                (argsRev, NxtArgBuilderState(char :: partRev, specialStack, nameOfArg))
            
            // no special sequence sequence
            case NxtArgBuilderState(partRev, Nil, nameOfArg) =>
                char match {
                    // end of positional arg
                    case ',' | EOL if nameOfArg.isEmpty => (PositionalArg(argsRev.length, toArg(partRev)) :: argsRev, NxtArgBuilderState())
                    
                    // end of named arg
                    case ',' | EOL if nameOfArg.nonEmpty => (NamedArg(nameOfArg, toArg(partRev)) :: argsRev, NxtArgBuilderState())

                    // getting the name of the arg
                    case '=' => (argsRev, NxtArgBuilderState(nameOfArg = toArg(partRev)))

                    // base case, add to the arg
                    case _ =>
                        (argsRev, NxtArgBuilderState(char :: partRev, Nil, nameOfArg))
                }
        }
    }

    argsReversed.reverse
}

def captureThineArguments(funcName: String): Regex = 
    s"""${funcName} *\\((.*)\\)""".r

def captureFirstInvocation(fullText: String, funcRegex: Regex): Option[List[PythonArg]] =
    funcRegex.findFirstMatchIn(fullText) map { raw => captureArgs(raw.group(1).trim()) }

val initializeRgx = captureThineArguments("\\.initialize")
val maxDistanceUptateRgx = captureThineArguments("\\.max_distance_update")

sealed trait SearchType { val name: String }
case object DynamicZipSearch extends SearchType { val name = "DynamicZipSearch" }
case object DynamicGeoSearch extends SearchType { val name = "DynamicGeoSearch" }

sealed trait InitArgs
case class CountryCodes(value: Set[String] = Set.empty) extends InitArgs
case class MaxCount(value: String) extends InitArgs 
case class MaxDistance(value: Double) extends InitArgs
case class Poison(cause: String) extends InitArgs

def extractCountryCodes(rawArg: String): CountryCodes =
    CountryCodes(delete_all_from(rawArg, Seq("list\\(","\\)","\\[","\\]")).split(",").toSet)

def captureVarAssignment(varName: String, inText: String): Option[String] = {
    val capturingRgx = s"""${varName} *= *(${floatingPointNum})""".r
    capturingRgx.findFirstMatchIn(inText) map { _.group(1) }
}

def lineStartIdx(text: String, inLineIdx: Int): Int =
    if (inLineIdx <= 0 || text(inLineIdx-1) == '\n') // at start of text, or at the head position
        inLineIdx
    else
        Range(inLineIdx-1, -1, -1) find (i => text(i) == '\n') map (_ + 1) getOrElse 0

def lineEndIdx(text: String, inLineIdx: Int): Int =
    Range(inLineIdx, text.length, 1) find (i => text(i) == '\n') getOrElse text.length

def lineWithIdx(inText: String, idxInLine: Int): String =
    inText.substring(lineStartIdx(inText, idxInLine), lineEndIdx(inText, idxInLine))

def indentOfLine(text: String, idx: Int): Option[Int] = {
    val lineStart = lineStartIdx(text, idx)
    val lineEnd = lineEndIdx(text, idx)

    val line = text.substring(lineStart, lineEnd).trim

    if (line.startsWith("#") || line.isEmpty)
        None
    else
        Range(lineStart, text.length, 1) find (i => text(i) != ' ' && text(i) != '\t') map { firstNonWhitespaceIdx =>
            firstNonWhitespaceIdx - lineStart
        }
}

def prevLineStartIdx(text: String, idx: Int): Int = lineStartIdx(text, lineStartIdx(text, idx) - 1)

def prevLine(text: String, aboveWhat: String): Option[String] =
    indexOfOpt(text, aboveWhat) map (i => lineWithIdx(text, prevLineStartIdx(text, i)))

def indexOfOpt(inText: String, ofWhat: String): Option[Int] = {
    val i = inText.indexOf(ofWhat)

    if (inText.isEmpty() || i == -1 || ofWhat.isEmpty())
        None
    else {
        val start = lineStartIdx(inText, i)
        val end = (start to inText.length()) find (c => List('#','\n').contains(inText(c))) getOrElse inText.length()

        if (inText.substring(start, end).contains(ofWhat))
            Some(i)
        else
            indexOfOpt(inText.splitAt(i)._1, ofWhat)
    }
}

def commentLine(containing: String, inText: String): String = {
    val i = inText.indexOf(containing)
    val startIdx = lineStartIdx(inText, i)
    val (a, b) = inText.splitAt(startIdx)
    a + "# " + b
}

def getVarName(identifyingString: String, inText: String): Option[String] =
    inText.lines.find(_.contains(identifyingString)) map { line =>
      line.split("=").head.trim
    }

def firstStartIdxOfLineWithSmallerIndent(idx: Int, indent: Int, text: String): Option[Int] =
    if (idx <= 0)
        None
    else
        indentOfLine(text, idx)
            .filter (_ < indent)
            .map (_ => lineStartIdx(text, idx))
            .orElse (firstStartIdxOfLineWithSmallerIndent(prevLineStartIdx(text, idx), indent, text))

def firstLineWithSmallerIndent(idx: Int, indent: Int, text: String): Option[String] =
    firstStartIdxOfLineWithSmallerIndent(idx, indent, text) map (i => lineWithIdx(text, i))

def findBlockStartIdx(aboveWhat: String, inText: String): Option[Int] =
    for {
        startIdx <- indexOfOpt(inText, aboveWhat)
        if startIdx > 0
        indentOfBlock <- indentOfLine(inText, startIdx) // orElse (prevLine(inText, aboveWhat).flatMap(findBlockStartIdx(_, inText)))
        blockStart <- firstStartIdxOfLineWithSmallerIndent(startIdx, indentOfBlock, inText)
    } yield blockStart

def findBlockStart(aboveWhat: String, inText: String): Option[String] =
    findBlockStartIdx(aboveWhat, inText) map (i => lineWithIdx(inText, i))


val ifStatementLineRgx = s"""^\\s*if.+ (.+):$$""".r
val elifStatementLineRgx = s"""^\\s*elif.+ (.+):$$""".r

def findIfOrElifUpperBlock(aboveWhat: String, inText: String): Option[String] =
    findBlockStart(aboveWhat, inText) flatMap {
        case ifStatementLineRgx(varOrLit) => 
            // println(s"IF ${varOrLit}")
            Some(varOrLit)
        case elifStatementLineRgx(varOrLit) => 
            // println(s"ELIF ${varOrLit}")
            Some(varOrLit)
        case e if e.contains("else") =>
            for {
                inLineIdx <- indexOfOpt(inText, e)
                prevLine = lineWithIdx(inText, prevLineStartIdx(inText, inLineIdx))
                recursiveResult <- findIfOrElifUpperBlock(prevLine, inText)
            } yield {
                // println(s"ELSE ${recursiveResult}")
                recursiveResult
            }
        case x =>
            // println(s"NONE: ${x}")
            None
    }

def findOnlyIfUpperBlock(aboveWhat: String, inText: String): Option[String] =
    findBlockStart(aboveWhat, inText) flatMap {
        case e if List("elif","else").exists(e.contains(_)) =>
            for {
                inLineIdx <- indexOfOpt(inText, e)
                prevLine = lineWithIdx(inText, prevLineStartIdx(inText, inLineIdx))
                recursiveResult <- findIfOrElifUpperBlock(prevLine, inText)
            } yield recursiveResult

        case e if e.contains("if") => Some(e)
        case x => None
    }

def captureInitArgs(fileText: String): List[InitArgs] = {
    val captureArgsHere = captureFirstInvocation(fileText, _)

    val initArgsOpt = captureArgsHere(initializeRgx)
    val maxDistanceArgsOpt = captureArgsHere(maxDistanceUptateRgx) flatMap (_.headOption)

    val initArgsParsed = initArgsOpt map { _ map {
            case PositionalArg(idx, value) =>
                idx match {
                    case 0 if value == "True" => CountryCodes(Set("'CA'"))
                    case 0  => CountryCodes(Set("'US'"))
                    case 1 => extractCountryCodes(value)
                }
            case NamedArg("include_canadian_fsas", value) => CountryCodes(Set("'CA'"))
            case NamedArg("country_codes", value) => extractCountryCodes(value)
        }
    } getOrElse Nil

    val initArgsCondensed = initArgsParsed.foldLeft(CountryCodes()) { (args, arg) =>
        args.copy(value = args.value ++ arg.value)
    }

    val maxDistanceArgsParsedOpt = maxDistanceArgsOpt flatMap {
        case PositionalArg(_, literal) =>
            if (literal.matches(floatingPointNum))
                Some(MaxDistance(literal.toDouble))
            else
                captureVarAssignment(literal, fileText) map { maxDist => MaxDistance(maxDist.toDouble) }
        
        case NamedArg(_, literal) if literal.matches(floatingPointNum) =>
            if (literal.matches(floatingPointNum))
                Some(MaxDistance(literal.toDouble))
            else
                captureVarAssignment(literal, fileText) map { maxDist => MaxDistance(maxDist.toDouble) }

        case PositionalArg(_, previouslyDefined) if previouslyDefined.matches("[a-zA-Z_]+") =>
            captureVarAssignment(previouslyDefined, fileText) map (m => MaxDistance(m.toDouble))

        case NamedArg(_, previouslyDefined) if previouslyDefined.matches("[a-zA-Z_]+") =>
            captureVarAssignment(previouslyDefined, fileText) map (m => MaxDistance(m.toDouble))
    }

    val maxCountOpt = for {
        varOrLit <- findIfOrElifUpperBlock(".max_distance_update(", fileText)
        lit <- if (varOrLit.matches("[a-zA-Z_]+")) captureVarAssignment(varOrLit, fileText) else Some(varOrLit)
    } yield {
        if (lit.matches("[0-9]+"))
            MaxCount(lit)
        else if (varOrLit.matches("[a-zA-Z_]+"))
            MaxCount(varOrLit)
        else
            throw new ExpectedException(s"Cannot capture max count from [${lit}]")
    }

    initArgsCondensed :: maxDistanceArgsParsedOpt.toList ::: maxCountOpt.toList
}

def whichSearchType (fileText: String): SearchType =
    (indexOfOpt(fileText, ".next_coord(").nonEmpty, indexOfOpt(fileText, ".next_zip(").nonEmpty) match {
        case (false, false) => throw ExpectedException("No next_coord nor next_zip detected!")
        case (true, true) => throw ExpectedException("Cannot have both next_coord and next_zip")
        case (true, false) => DynamicGeoSearch
        case (false, true) => DynamicZipSearch
    }

def subText(fileText: String): String = {

    val args = captureInitArgs(fileText) map {
            case CountryCodes(value) => s"country_codes=[${value.mkString(",")}]"
            case MaxCount(value) => s"max_search_results=${value}"
            case MaxDistance(value) => s"max_radius_miles=${value}"
    } mkString(", ")

    val searchType = whichSearchType(fileText)

    val properCtor = s"${searchType.name}(${args})"

    val searchVarName = getVarName("ClosestNSearch()", fileText).get

    val withSimpleSubs = fileText
                    .replaceAll("""ClosestNSearch\(\)""", properCtor)
                    .replaceAll("max_search_results=0", "max_search_results=None")
                    .replaceAll("max_radius_miles=0", "max_radius_miles=None")
                    .replaceAll("ClosestNSearch", searchType.name)    // <- import
                    .replaceAll(""".initialize\(.*\)""", ".initialize()")
                    .replaceAll("""\.next_zip\(\)""", ".next()")      // <- only one of these two is ever present
                    .replaceAll("""\.next_coord\(\)""", ".next()")    // <- ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    .replaceAll("""\.current_zip""", "._search.current_zip") // <- oh well...

    val updateWith = indexOfOpt(withSimpleSubs, ".max_count_update(")
                        .flatMap { _ => """\.max_count_update\((.+)\)""".r.findFirstMatchIn(withSimpleSubs) }
                        .map(_.group(1))
                        .getOrElse("[]")

    val updateCalls = List(""".max_count_update(""", """.max_distance_update(""")

    val findUpdateLine = updateCalls.find(c => indexOfOpt(withSimpleSubs, c).nonEmpty) match {
        case None => throw ExpectedException("no max_count_update or max_distance_update detected!")
        case Some(value) => value
    }

    // val upperBlockIdx = (findOnlyIfUpperBlock(findUpdateLine, withSimpleSubs) flatMap (indexOfOpt(withSimpleSubs, _)))
    //                         .orElse(indexOfOpt(withSimpleSubs, findUpdateLine) map (prevLineStartIdx(withSimpleSubs, _)) filter { i =>
    //                             val prev = lineWithIdx(withSimpleSubs, i).trim
    //                             prev.nonEmpty && !prev.startsWith("#")
    //                         })

    // upperBlockIdx map (i => println(">!", lineWithIdx(withSimpleSubs, i)))

    val updateWithGeneric = """ *if .+:\n.+\.max_count_update\(.+\)\s*\n\s*else:\s*\n\s*.+\.max_distance_update\(.+\) *"""

    val withUpdate = withSimpleSubs.replaceAll(updateWithGeneric, s"\n${searchVarName}.update_with(${updateWith})\n")

    //  upperBlockIdx match {
    //     case Some(idx) =>
    //         val indentInt = indentOfLine(withSimpleSubs, idx).get
    //         val indent = (1 to indentInt).map(_ => " ").mkString("")
    //         val updatePlacementIdx = prevLineStartIdx(withSimpleSubs, idx)
            
    //         val (preUpd, postUpd) = withSimpleSubs.splitAt(updatePlacementIdx)
    //         preUpd + s"${indent}${searchVarName}.update_with(${updateWith})\n" + postUpd

    //     case None =>
    //         withSimpleSubs.replaceFirst(".max_count_update\\((.+)\\)", s".update_with(${updateWith})")
    // }
    
    val withCommentedUpdates = updateCalls.foldLeft(withUpdate) { 
        (accum, next) => commentLine(next, accum)
    }

    withCommentedUpdates + "\n" // append newline at EOF
}

val counter = new AtomicInteger(0)
val failed = new AtomicInteger(0)

val newScripts = """ClosestNSearch\(\)(?! # TODO: OLD VERSION)""".r

lazy val program = allScrapersWithSgZip foreach { dir =>
    all_python_scripts_in_dir(dir) map (s => File(s.toString)) filter { s =>
        newScripts.findFirstIn(s.contentAsString).nonEmpty
    } foreach { scraper: File =>
        try {
            throw new ExpectedException("Intentionally freezing version")
            println(s"Processing [${counter.addAndGet(1)}]: ${scraper}")
            val newText = subText(python_code_lines_from(scraper).mkString("\n"))
            scraper.overwrite(newText)
        } catch {
            case ExpectedException(reason) =>
                println(s">>[Failure: ${failed.addAndGet(1)}] [${scraper}] Failed with: [${reason}] Freezing sgzip==0.0.55")
                requirements_txt_in_dir(dir) map { reqfile =>
                    delete_from_reqs(reqfile, "sgzip")
                    insert_in_reqs(reqfile, "sgzip==0.0.55")
                }
                
                scraper.overwrite(
                    scraper.contentAsString.replaceAll("""ClosestNSearch\(\)""", "ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!")
                )

            case e: Exception =>
                println(s">>[Failure: ${failed.addAndGet(1)}] [${scraper}] !!! Unexpected exception !!! Freezing sgzip==0.0.55")
                e.printStackTrace()

                requirements_txt_in_dir(dir) map { reqfile =>
                    delete_from_reqs(reqfile, "sgzip")
                    insert_in_reqs(reqfile, "sgzip==0.0.55")
                }
        }
    }
}

@main
def run (x: Boolean) {
    println(s">> Running program")
    program
    println (s">> Failures / Overall ${failed.get()} / ${counter.get()}")
}