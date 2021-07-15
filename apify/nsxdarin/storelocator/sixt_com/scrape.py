import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import cloudscraper

session = SgRequests()
scraper = cloudscraper.create_scraper(sess=session)

logger = SgLogSetup().get_logger("sixt_com")


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
    states = []
    url = "https://www.sixt.com/car-rental/#/"
    r = scraper.get(url)
    website = "sixt.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'States</span> </div> <div class="content"> <ul class="list">' in line:
            info = line.split(
                'States</span> </div> <div class="content"> <ul class="list">'
            )[1].split("<span>Europe")[0]
            items = info.split('<a href="/car-rental/usa/')
            for item in items:
                if 'target="_self">' in item:
                    states.append(
                        "https://www.sixt.com/car-rental/usa/" + item.split('"')[0]
                    )
    for state in states:
        logger.info(state)
        r2 = scraper.get(state)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'locationLink: "' in line2:
                items = line2.split('locationLink: "')
                for item in items:
                    if "coordinates:" in item:
                        locs.append("https://www.sixt.com" + item.split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        r2 = scraper.get(loc)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<h1>" in line2:
                name = line2.split("<h1>")[1].split("<")[0].strip()
            if "orlando-lake-buena-vista" in loc:
                add = "12205 S Apopka Vineland Rd"
                city = "Orlando"
                state = "FL"
                zc = "32836-6804"
                lat = "28.386945724487"
                lng = "-81.504974365234"
                hours = "MO - FR: 07:00 - 18:00; SA - SU: 09:00 - 17:00"
            if '"@id": "' in line2:
                state = "<MISSING>"
                try:
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                    city = line2.split('"addressLocality":"')[1].split('"')[0]
                    lat = line2.split(',"latitude":')[1].split(",")[0]
                    lng = line2.split('"longitude":')[1].split("}")[0]
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    hours = (
                        line2.split('"openingHours":["')[1]
                        .split('"]')[0]
                        .replace('","', "; ")
                    )
                except:
                    pass
            if "address</h3>" in line2 and add == "":
                addinfo = (
                    line2.split("<p>")[1].split("<")[0].replace(", Suite", " Suite")
                )
                add = addinfo.split(",")[0]
                zc = addinfo.split(",")[1].strip().split(" ")[0]
                try:
                    city = addinfo.split(",")[1].strip().split(" ")[1]
                except:
                    city = "<MISSING>"
            if "coordinates: { lat:" in line2:
                lat = line2.split("coordinates: { lat:")[1].split(",")[0].strip()
                lng = (
                    line2.split("coordinates: { lat:")[1]
                    .split("lng:")[1]
                    .split(",")[0]
                    .strip()
                )
            if 'openhours-scheduler_week">' in line2:
                hours = (
                    line2.split('openhours-scheduler_week">')[1]
                    .split("</p> </div>")[0]
                    .replace('<div data-component="text">', "")
                    .replace("<p>", "")
                    .replace("</div>", "")
                    .replace("<div>", "")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                )
        hours = hours.replace("24 HRS RETURN;", "").strip()
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
    locs = []
    states = []
    url = "https://www.sixt.com/car-rental/united-kingdom/#/"
    r = scraper.get(url)
    website = "sixt.com"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<div class="swiper-wrapper"> <a href="/car-rental/united-kingdom/' in line:
            info = line.split('<div class="swiper-wrapper">')[1]
            items = info.split('<a href="/car-rental/united-kingdom/')
            for item in items:
                if 'target="_self"' in item:
                    states.append(
                        "https://www.sixt.com/car-rental/united-kingdom/"
                        + item.split('"')[0]
                    )
    for state in states:
        logger.info(state)
        r2 = scraper.get(state)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'locationLink: "' in line2:
                items = line2.split('locationLink: "')
                for item in items:
                    if "coordinates:" in item:
                        locs.append("https://www.sixt.com" + item.split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        r2 = scraper.get(loc)
        try:
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if '"@id": "' in line2:
                    name = line2.split("<h1>")[1].split("<")[0].strip()
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                    city = line2.split('"addressLocality":"')[1].split('"')[0]
                    lat = line2.split(',"latitude":')[1].split(",")[0]
                    lng = line2.split('"longitude":')[1].split("}")[0]
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    hours = (
                        line2.split('"openingHours":["')[1]
                        .split('"]')[0]
                        .replace('","', "; ")
                    )
        except:
            pass
        if "hilton-park-lane" in loc:
            name = "LONDON PARK LANE CAR RENTAL"
            add = "22 Park Lane"
            state = "<MISSING>"
            zc = "W1K 1BE"
            city = "London"
            lat = "51.155784606934"
            lng = "-0.15942700207233"
            hours = "24 HRS RETURN; MO - FR: 08:00 - 16:00; SA - SU: 08:00 - 13:00; BANK HOLIDAY: 08:00 - 13:00"
        if "n/london-wembley" in loc:
            name = "LONDON WEMBLEY (NORTH) CAR RENTAL"
            add = "GEC Est. Courtenay Rd.,East Ln"
            state = "<MISSING>"
            zc = "HA9 7ND"
            city = "London"
            lat = "51.155784606934"
            lng = "-0.15942700207233"
            hours = "24 HRS RETURN; MO - FR: 08:00 - 18:00; SA - SU: 08:00 - 13:00; BANK HOLIDAY: 08:00 - 13:00"
        hours = hours.replace("24 HRS RETURN;", "").strip()
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
