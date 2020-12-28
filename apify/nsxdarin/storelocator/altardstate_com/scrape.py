import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("altardstate_com")


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
    url = "https://www.altardstate.com/on/demandware.store/Sites-altardstate-Site/default/Stores-FindStores?showMap=true&radius=5000&postalCode=55441&radius=300"
    r = session.get(url, headers=headers)
    website = "altardstate.com"
    typ = "<MISSING>"
    loc = "<MISSING>"
    country = "US"
    Found = False
    name = ""
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"locale": "' in line or '"inventoryListId":' in line:
            Found = True
        if Found and '"ID": "' in line:
            store = line.split('"ID": "')[1].split('"')[0]
            Found = False
        if '"name": "' in line:
            name = line.split('"name": "')[1].split('"')[0]
        if '"address1": "' in line:
            add = line.split('"address1": "')[1].split('"')[0]
        if '"city": "' in line:
            city = line.split('"city": "')[1].split('"')[0]
        if '"postalCode": "' in line:
            zc = line.split('"postalCode": "')[1].split('"')[0]
        if '"latitude": ' in line:
            lat = line.split('"latitude": ')[1].split(",")[0]
        if '"longitude": ' in line:
            lng = line.split('"longitude": ')[1].split(",")[0]
        if '"stateCode": "' in line:
            state = line.split('"stateCode": "')[1].split('"')[0]
        if '"countryCode": "' in line:
            country = line.split('"countryCode": "')[1].split('"')[0]
        if '"phone": "' in line:
            phone = line.split('"phone": "')[1].split('"')[0]
        if '"storeHours": "' in line:
            hours = line.split('"storeHours": "')[1].split('"')[0]
            hours = (
                hours.replace("<br />", "; ").replace("\\n", "").replace("&nbsp;", " ")
            )
            hours = hours.replace("<p>", "").replace("</p>", "")
            if "details. " in hours:
                hours = hours.split("details. ")[1]
        if "BRIDGE STREET" in name:
            hours = "Sun: Noon-6PM; Mon-Sat: 11AM-7PM"
        if "WEST TOWN MALL" in name:
            hours = "Sun-Thu: 11AM-7PM; Fri-Sat: 11AM-8PM"
        if "THE PINNACLE AT TURKEY CREEK" in name:
            hours = "Sun: Noon-6PM; Mon-Sat: 11AM-7PM"
        if '"storebrands": ' in line:
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
