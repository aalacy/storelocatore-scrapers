import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("uk_louisvuitton_com")


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
    url = "https://uk.louisvuitton.com/ajax/getStoreJson.jsp?storeLang=eng-gb&cache=NoStore&pageType=storelocator_section&flagShip=false&latitudeCenter=50.952972788639634&longitudeCenter=3.769909094726529&latitudeA=60.754929887896296&longitudeA=-28.772281457031283&latitudeB=38.54139371919008&longitudeB=36.31209964648434&doClosestSearch=false&zoomLevel=4&country=&categories=&clickAndCollect=false&productId=&countryId=&osa=null&Ntt=undefined"
    r = session.get(url, headers=headers)
    website = "uk.louisvuitton.com"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["stores"]:
        hours = ""
        store = item["storeId"]
        lat = item["latitude"]
        lng = item["longitude"]
        name = item["name"]
        add = item["street"]
        city = item["city"]
        state = "<MISSING>"
        country = item["country"]
        zc = item["zip"]
        loc = item["url"]
        r2 = session.get(loc, headers=headers)
        for line in r2.iter_lines():
            line = str(line.decode("utf-8"))
            if '"street":"' in line:
                add = line.split('"street":"')[1].split('"')[0]
        phone = item["phone"]
        for day in item["openingHours"]:
            hrs = day["openingDay"] + ": " + day["openingHour"]
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
        hours = hours.replace(" / ", "-")
        if "0" not in hours:
            hours = "<MISSING>"
        if " - " in name:
            name = name.split(" - ")[0]
        if "(" in phone:
            phone = phone.split("(")[0].strip()
        if country == "United Kingdom":
            country = "GB"
            add = add.replace("&#039;", "'")
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
