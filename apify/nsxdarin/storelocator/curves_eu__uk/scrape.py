import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrf-token": "oTBAeL4RNVfHnNoYMzvYGyK5ZsgKQEPJj8JY6TdR0fDgRmCg3nLkLOFgH2HZVoXjUcoU25RvPAMb0BSIa0uKIA==",
    "x-requested-with": "XMLHttpRequest",
}

logger = SgLogSetup().get_logger("curves_eu__uk")


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
    url = "http://www.curves.eu/uk/clubs.js?join=false"
    r = session.get(url, headers=headers)
    website = "curves.eu/uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ">View details</a>" in line:
            locs.append("http://www.curves.eu/" + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        addinfo = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        AFound = False
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<h1>" in line2:
                name = line2.split(">")[1].split("<")[0]
            if "data-latitude='" in line2:
                lat = line2.split("data-latitude='")[1].split("'")[0]
                lng = line2.split("data-longitude='")[1].split("'")[0]
            if "href='tel:" in line2:
                phone = line2.split("href='tel:")[1].split("'")[0]
            if "day</td>" in line2:
                day = line2.split(">")[1].split("<")[0]
                g = next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                g = g.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                hrs = day + ": " + g
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "<address>" in line2:
                AFound = True
            if AFound and "United Kingdom<br>" in line2:
                AFound = False
            if AFound and "<a class='tel'" in line2:
                AFound = False
            if AFound and "<br>" in line2:
                info = line2.split("<")[0].strip()
                if addinfo == "":
                    addinfo = info
                else:
                    addinfo = addinfo + ", " + info
        if addinfo.count(",") == 2:
            add = addinfo.split(",")[0]
            zc = addinfo.split(",")[1].strip()
            city = addinfo.split(",")[2].strip()
        if addinfo.count(",") == 3:
            add = addinfo.split(",")[0] + " " + addinfo.split(",")[1].strip()
            zc = addinfo.split(",")[2].strip()
            city = addinfo.split(",")[3].strip()
        if addinfo.count(",") == 4:
            add = (
                addinfo.split(",")[0]
                + " "
                + addinfo.split(",")[1].strip()
                + " "
                + addinfo.split(",")[2].strip()
            )
            zc = addinfo.split(",")[3].strip()
            city = addinfo.split(",")[4].strip()
        name = name.replace("&amp;", "&").replace(", UK", "")
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
