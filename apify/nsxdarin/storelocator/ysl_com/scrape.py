import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ysl_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    ccodes = []
    url_home = "https://www.ysl.com/en-us/storelocator"
    r = session.get(url_home, headers=headers)
    Found = False
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "Select a Region / Country" in line:
            Found = True
        if Found and '<option value="' in line and "Select a Region" not in line:
            ccodes.append(line.split('<option value="')[1].split('"')[0])
        if Found and '<div class="c-form__error"></div>' in line:
            Found = False
    website = "ysl.com"
    typ = "<MISSING>"
    for ccode in ccodes:
        url = (
            "https://www.ysl.com/on/demandware.store/Sites-SLP-NOAM-Site/en_US/Stores-FindStoresData?countryCode="
            + ccode
        )
        r = session.get(url, headers=headers)
        country = ccode
        logger.info("Pulling Country %s" % ccode)
        for item in json.loads(r.content)["storesData"]["stores"]:
            store = item["ID"]
            name = item["name"]
            add = item["address1"]
            city = item["city"]
            zc = item["postalCode"]
            state = item["stateCode"]
            phone = item["phone"]
            lat = item["latitude"]
            lng = item["longitude"]
            loc = item["detailsUrl"]
            hours = "Sun: " + item["sunHours"]
            hours = hours + "; Mon: " + item["monHours"]
            hours = hours + "; Tue: " + item["tueHours"]
            hours = hours + "; Wed: " + item["wedHours"]
            hours = hours + "; Thu: " + item["thuHours"]
            hours = hours + "; Fri: " + item["friHours"]
            hours = hours + "; Sat: " + item["satHours"]
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
