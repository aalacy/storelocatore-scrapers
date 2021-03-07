import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dairyqueen_com")


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
    url = "https://www.dairyqueen.com/en-us/sitemap/sitemap-en-us.xml"
    r = session.get(url, headers=headers)
    website = "dairyqueen.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.dairyqueen.com/en-us/locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        lurl = (
            "https://www.dairyqueen.com/api/vtl/location-detail-schema?storeId=" + store
        )
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"amenities"' in line2:
                name = line2.split('{"address1":"')[1].split('"')[0]
                add = line2.split('"address3":"')[1].split('"')[0]
                lat = line2.split('"latlong":"')[1].split('"')[0].split(",")[0]
                lng = line2.split('"latlong":"')[1].split('"')[0].split(",")[1]
                city = line2.split('"city":"')[1].split('"')[0]
                try:
                    phone = line2.split('"phone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                state = line2.split('"stateProvince":"')[1].split('"')[0]
                try:
                    hours = line2.split('"storeHours":"1:')[1].split('"')[0]
                    hours = "Sun: " + hours
                    hours = hours.replace(",2:", "; Mon: ")
                    hours = hours.replace(",3:", "; Tue: ")
                    hours = hours.replace(",4:", "; Wed: ")
                    hours = hours.replace(",5:", "; Thu: ")
                    hours = hours.replace(",6:", "; Fri: ")
                    hours = hours.replace(",7:", "; Sat: ")
                except:
                    hours = "<MISSING>"
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                name = line2.split('"address1":"')[1].split('"')[0]
        if phone == "":
            phone = "<MISSING>"
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
