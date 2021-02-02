import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("uk_tumi_com")


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
    url = "https://uk.tumi.com/on/demandware.store/Sites-tumi-Site/en_GB/StoreLocator-GetResults?lat=53.8007554&lng=-1.5490774&country=gb&types=outlet&radius=2000&format=json"
    r = session.get(url, headers=headers)
    website = "uk.tumi.com"
    typ = "Outlet"
    country = "GB"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"ID":"' in line:
            items = line.split('{"ID":"')
            for item in items:
                if ',"address1":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    add = (
                        item.split(',"address1":"')[1].split('"')[0]
                        + " "
                        + item.split('"address2":"')[1].split('"')[0]
                    )
                    city = item.split('"city":"')[1].split('"')[0]
                    state = "<MISSING>"
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    phone = item.split("Store:")[1].split('"')[0].strip()
                    if "closed" in name.lower():
                        hours = "Temporarily Closed"
                    else:
                        hours = item.split('"storeHoursJson":"')[1].split(
                            '}","website'
                        )[0]
                        hours = (
                            hours.replace(',\n        "', "; ")
                            .replace('"')[0]
                            .replace("\\", "")
                            .replace("[", "")
                            .replace("]", "")
                            .strip()
                        )
                        hours = (
                            hours.replace("\\t", "").replace("\\n", "").replace("}", "")
                        )
                    if " - Temporarily closed" in name:
                        name = name.split(" - Temporarily closed")[0]
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
    url = "https://uk.tumi.com/on/demandware.store/Sites-tumi-Site/en_GB/StoreLocator-GetResults?lat=53.8007554&lng=-1.5490774&country=gb&types=brandstore&radius=2000&format=json"
    r = session.get(url, headers=headers)
    website = "uk.tumi.com"
    typ = "Brandstore"
    country = "GB"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"ID":"' in line:
            items = line.split('{"ID":"')
            for item in items:
                if ',"address1":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    add = (
                        item.split(',"address1":"')[1].split('"')[0]
                        + " "
                        + item.split('"address2":"')[1].split('"')[0]
                    )
                    city = item.split('"city":"')[1].split('"')[0]
                    state = "<MISSING>"
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    try:
                        phone = item.split("Store:")[1].split('"')[0].strip()
                    except:
                        phone = "<MISSING>"
                    if "closed" in name.lower():
                        hours = "Temporarily Closed"
                    else:
                        hours = item.split('"storeHoursJson":"')[1].split(
                            '}","website'
                        )[0]
                        hours = (
                            hours.replace(',\n        "', "; ")
                            .replace('"')[0]
                            .replace("\\", "")
                            .replace("[", "")
                            .replace("]", "")
                            .strip()
                        )
                        hours = (
                            hours.replace("\\t", "").replace("\\n", "").replace("}", "")
                        )
                    if " - Temporarily closed" in name:
                        name = name.split(" - Temporarily closed")[0]
                    if "Westfield" in add:
                        phone = "+44 2 087403296"
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
