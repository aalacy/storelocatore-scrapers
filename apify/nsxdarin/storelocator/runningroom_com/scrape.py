import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("runningroom_com")


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
    adds = []
    locs = []
    cities = []
    url = "https://www.runningroom.com/ca/inside.php?id=3033"
    r = session.get(url, headers=headers)
    website = "runningroom.com"
    typ = "<MISSING>"
    country = "CA"
    Found = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "Canada</h3>" in line:
            Found = True
        if Found and "Store Openings</h3>" in line:
            Found = False
        if Found and "inside.php" in line:
            cities.append(line.split('href="')[1].split('"')[0])
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if (
                '<p><a href="https://www.runningroom.com/hm/' in line2
                and "Find<" not in line2
            ):
                locs.append(line2.split('href="')[1].split('"')[0])
            if (
                '<p><a href="https://www.runningroom.com/ca/' in line2
                and "Find<" not in line2
            ):
                locs.append(line2.split('href="')[1].split('"')[0])
            if (
                '<p> <a href="https://www.runningroom.com/ca/' in line2
                and "Find<" not in line2
            ):
                locs.append(line2.split('href="')[1].split('"')[0])
            if (
                '<p> <a href="https://www.runningroom.com/hm/' in line2
                and "Find<" not in line2
            ):
                locs.append(line2.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("id=")[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        AFound = False
        SFound = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "Store Hours</h3>" in line2 and hours == "":
                SFound = True
            if (
                SFound
                and "</p>" in line2
                and "-->" not in line2
                and "Temporarily Closed" not in line2
            ):
                SFound = False
            if SFound and "p.m." in line2 and "--" not in line2:
                hrs = (
                    line2.replace("<br>", "")
                    .replace("<p>", "")
                    .strip()
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if SFound and "--" in line2 and hours != "":
                SFound = False
            if '<h2 class="page_title">' in line2:
                name = line2.split('<h2 class="page_title">')[1].split("<")[0]
            if "<h3>Address</h3>" in line2:
                AFound = True
            if AFound and ", " in line2 and "<" in line2:
                if (
                    ", AB" in line2
                    or ", SK" in line2
                    or ", QC" in line2
                    or ", BC" in line2
                    or ", ON" in line2
                    or ", NS" in line2
                    or ", PE" in line2
                    or ", MB" in line2
                    or ", MN" in line2
                    or ", HI" in line2
                ):
                    if "2326" in loc:
                        city = "Kitchener"
                        state = "ON"
                        zc = "N2C 1X3"
                    elif "4612" in loc:
                        city = "Montreal"
                        state = "QC"
                        zc = "H4N 1J8"
                    else:
                        addinfo = line2.split("<")[0]
                        city = addinfo.split(",")[0]
                        state = addinfo.split(",")[1].strip().split(" ")[0]
                        zc = addinfo.split(",")[1].strip().split(" ", 1)[1]
                    AFound = False
            if AFound and "<br>" in line2:
                ainfo = line2.replace("<p>", "").split("<")[0].strip()
                if add == "":
                    add = ainfo
                else:
                    add = add + " " + ainfo
                    add = add.strip()
            if "Ph:" in line2:
                AFound = False
                phone = line2.split("Ph:")[1].split("<")[0].strip()
            if '<iframe src="https://www.google.com/maps/' in line2:
                lat = line2.split("!3d")[1].split("!")[0]
                lng = line2.split("!2d")[1].split("!")[0]
        if hours == "":
            hours = "<MISSING>"
        if state == "MN" or state == "HI":
            country = "US"
        else:
            country = "CA"
        if "2449" in loc:
            add = "300 Main Street"
            city = "Moncton"
            state = "NB"
            zc = "E1C 1B9"
            phone = "(506) 386-6002"
        if "2447" in loc:
            add = "449 King Street"
            city = "Fredericton"
            state = "NB"
            zc = "E3B 1E5"
            phone = "(506) 459-4440"
        if "2469" in loc:
            add = "#9 Rowan Street"
            city = "St. Johns"
            state = "NL"
            zc = "A1B 2X2"
            phone = "(709) 738-3433"
        if "2388" in loc:
            add = "3065 Bloor St. West"
            city = "Toronto"
            state = "ON"
            zc = "M8X 1C6"
            phone = "(416) 207-0033"
        if "3177" in loc:
            add = "11639 - Fountains Drive"
            city = "Maple Grove"
            state = "MN"
            zc = "55369"
            phone = "(763) 425-0610"
        if phone == "":
            phone = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if lng == "":
            lng = "<MISSING>"
        if "2410" in loc:
            phone = "(519) 747-4800"
        if "2372" in loc:
            phone = "(705) 523-4664"
        if "3645" in loc:
            phone = "(905) 726-1600"
        if "5102" in loc:
            add = "582 chemin de Touraine suite 502"
            city = "Boucherville"
            state = "QC"
            country = "CA"
            zc = "J4B 5E4"
            phone = "(450) 641-8223"
        if "3177" in loc:
            country = "US"
        if "6655-" in add:
            add = "6655-178 Street"
        add = add.replace("Cedar Pointe Plaza ", "")
        add = add.replace("Country Club Centre ", "")
        add = add.replace("Faubourg Boisbriand ", "")
        add = add.replace("Glenmore Landing Shopping Centre ", "")
        add = add.replace("Grant Crossing Running Room 5 - ", "")
        add = add.replace("Kenaston Village Mall ", "")
        add = add.replace("Murano South Tower Condominium ", "")
        add = add.replace("Quartiers Dix 30 ", "")
        add = add.replace("Rocky View, Alberta ", "")
        add = add.replace("Southpointe Common ", "")
        add = add.replace("Thickson Place ", "")
        add = add.replace("Toronto-Dominion Centre ", "")
        add = add.replace("Tsawwassen Mills ", "")
        add = add.replace("Uptown Running Room ", "")
        add = add.replace("Westwood Centre #202 - ", "")
        if add != "":
            if add not in adds:
                adds.append(add)
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
