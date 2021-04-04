import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("havertys_com")


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
    url = "https://www.havertys.com/furniture/allstores"
    r = session.get(url, headers=headers)
    website = "havertys.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "Store details</a>" in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl not in locs:
                locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        HFound = False
        hours = ""
        CS = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "center: {lat: " in line2:
                lat = line2.split("center: {lat: ")[1].split(",")[0]
                lng = line2.split("lng: ")[1].split("}")[0]
            if "var address = '" in line2:
                add = line2.split("var address = '")[1].split("'")[0]
            if "var name = '" in line2:
                name = line2.split("var name = '")[1].split("'")[0]
            if "var city = '" in line2:
                city = line2.split("var city = '")[1].split("'")[0]
            if "var state = '" in line2:
                state = line2.split("var state = '")[1].split("'")[0]
            if "var zip = '" in line2:
                zc = line2.split("var zip = '")[1].split("'")[0]
            if "var phone = '" in line2:
                phone = line2.split("var phone = '")[1].split("'")[0]
            if "Showroom Hours" in line2:
                HFound = True
            if HFound and "class" in line2:
                HFound = False
            if HFound and "</div>" in line2:
                HFound = False
            if HFound and "</span>" in line2:
                hrs = line2.split(">")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "<span>Coming soon</span>" in line2:
                CS = True
        if CS is False:
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
