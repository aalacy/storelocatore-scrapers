import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("www.englishgolf-courses_co_uk")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    locs = []
    url = "https://www.englishgolf-courses.co.uk/atoz.html"
    r = session.get(url, headers=headers)
    website = "englishgolf-courses.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'padding-top:5px;">' in line:
            if "villa.php" not in line:
                locs.append(
                    "https://www.englishgolf-courses.co.uk"
                    + line.split('href="')[1].split('"')[0]
                )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8", errors="replace"))
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if "Address: " in line2:
                addinfo = (
                    line2.split("Address: ")[1]
                    .split("<")[0]
                    .replace("\t", "")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .strip()
                )
                addinfo = (
                    addinfo.replace("Road", "Road,")
                    .replace("Brentwood", "Brentwood,")
                    .replace("Essex", "Essex,")
                )
                addinfo = (
                    addinfo.replace("LaneB", "Lane, B")
                    .replace("leySurrey", "ley, Surrey")
                    .replace("reyRH", "rey, RH")
                )
                addinfo = (
                    addinfo.replace("Hill", "Hill,")
                    .replace("Calne", "Calne,")
                    .replace("Wiltshire", "Wiltshire,")
                )
                addinfo = (
                    addinfo.replace("LtdHud", "Ltd, Hud")
                    .replace("fieldWest", "field, West")
                    .replace("YorkshireHD", "Yorkshire, HD")
                )
                addinfo = (
                    addinfo.replace("waySh", "way,Sh")
                    .replace("eldSouth", "eld,South")
                    .replace("Yorks S17", "Yorks, S17")
                )
                addinfo = addinfo.replace("down Dorest", "down, Dorset").replace(
                    "Dorset BH", "Dorset, BH"
                )
                addinfo = addinfo.replace("Bar Mer", "Bar, Mer").replace(
                    "side WA", "side, WA"
                )
                addinfo = addinfo.replace("wich Man", "wich, Man").replace(
                    "ter M25", "ter, M25"
                )
                addinfo = (
                    addinfo.replace("EstateHen", "Estate, Hen")
                    .replace("MarlowBucks", "Marlow,Bucks")
                    .replace("cksSL7", "cks,SL7")
                )
                addinfo = addinfo.replace("Studland S", "Studland, S").replace(
                    "age BH19", "age, BH19"
                )
                addinfo = addinfo.replace("ster Worce", "ster, Worce").replace(
                    "shireDY", "shire, DY"
                )
                addinfo = (
                    addinfo.replace("Reach C", "Reach, C")
                    .replace("sey Surrey", "sey, Surrey")
                    .replace("Surrey KT", "Surrey, KT")
                )
                addinfo = addinfo.replace("NelsonLan", "Nelson, Lan").replace(
                    "shireBB", "shire, BB"
                )
                addinfo = (
                    addinfo.replace("tonKing", "ton, King")
                    .replace("LynnNor", "Lynn,Nor")
                    .replace("folkPE", "folk,PE")
                )
                addinfo = addinfo.replace(
                    "Caterham Surrey", "Caterham, Surrey"
                ).replace("Surrey CR", "Surrey, CR")
                addinfo = addinfo.replace("Grove White", "Grove, White").replace(
                    "Manchester M45", "Manchester, M45"
                )
                addinfo = (
                    addinfo.replace("CorfeTaun", "Corfe,Taun")
                    .replace("tonSomer", "ton,Somer")
                    .replace("setTA", "set, TA")
                )
                addinfo = addinfo.replace("Brinkworth Wilt", "Brinkworth, Wilt")
                addinfo = (
                    addinfo.replace("Law Dod", "Law, Dod")
                    .replace("ton Wooler", "ton, Wooler")
                    .replace("er NE71", "er, NE71")
                )
                addinfo = addinfo.replace(",,", ",")
                if addinfo.count(",") == 2:
                    add = "<MISSING>"
                    city = addinfo.split(",")[0].strip()
                    state = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                elif addinfo.count(",") == 3:
                    add = addinfo.split(",")[0]
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip()
                    zc = addinfo.split(",")[3].strip()
                elif addinfo.count(",") == 4:
                    add = addinfo.split(",")[0]
                    add = add + " " + addinfo.split(",")[1].strip()
                    city = addinfo.split(",")[2].strip()
                    state = addinfo.split(",")[3].strip()
                    zc = addinfo.split(",")[4].strip()
                else:
                    add = addinfo.split(",")[0].strip()
                    add = add + " " + addinfo.split(",")[1].strip()
                    add = add + " " + addinfo.split(",")[2].strip()
                    city = addinfo.split(",")[3].strip()
                    state = addinfo.split(",")[4].strip()
                    zc = addinfo.split(",")[5].strip()
            if phone == "" and "Tel: " in line2:
                phone = (
                    line2.split("Tel: ")[1].split("&nbsp")[0].strip().replace("\t", "")
                )
        add = (
            add.replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
        )
        add = add.replace("\t", "")
        if city == "":
            city = state
            state = "<MISSING>"
        if zc == "":
            zc = "<MISSING>"
        if zc.count(" ") == 2:
            zc = zc.split(" ")[1] + " " + zc.split(" ")[2]
        if zc.count(" ") == 3:
            zc = zc.split(" ")[2] + " " + zc.split(" ")[3]
        if zc.count(" ") == 4:
            zc = zc.split(" ")[3] + " " + zc.split(" ")[4]
        yield [
            website,
            loc,
            name,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
