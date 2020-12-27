import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ilovedirtcheap_com")


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
    url = "https://ilovedirtcheap.com/locations/"
    r = session.get(url, headers=headers)
    website = "ilovedirtcheap.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<div class='buttons'><a href='" in line:
            locs.append(line.split("<div class='buttons'><a href='")[1].split("'")[0])
    for loc in locs:
        logger.info(loc)
        HFound = False
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        store = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if "LatLng(" in line2:
                lat = line2.split("LatLng(")[1].split(",")[0]
                lng = line2.split("LatLng(")[1].split(",")[1].split(")")[0]
            if "<p class='address'>" in line2:
                add = line2.split("<p class='address'>")[1].split("<")[0]
                city = line2.split("<br/>")[1].split(",")[0]
                state = line2.split("<br/>")[1].split(",")[1].strip().split(" ")[0]
                zc = line2.split("<br/>")[1].rsplit(" ", 1)[1]
                phone = line2.split("<br/>")[2].split("<")[0]
            if "https://app.dirtcheapalerts.com/api/get_website_alerts/" in line2:
                store = line2.split(
                    "https://app.dirtcheapalerts.com/api/get_website_alerts/"
                )[1].split("/")[0]
            if "Hours</h3>" in line2:
                HFound = True
            if HFound and "pm<br />" not in line2 and "Hours</h3>" not in line2:
                HFound = False
            if HFound and "<br />" in line2:
                hrs = line2.replace("<p>", "").replace("</p>", "").split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if "dirt-cheap-corporate-office" in loc:
            hours = "9am-8pm, Mon-Sat; 12pm-7pm Sunday"
        hours = hours.replace("\t", "").strip()
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
