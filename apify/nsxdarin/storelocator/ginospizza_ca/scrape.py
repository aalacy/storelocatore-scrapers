import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ginospizza_ca")


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
    markers = []
    url = "https://ginospizza.ca/locations/"
    r = session.get(url, headers=headers)
    website = "ginospizza.ca"
    typ = "<MISSING>"
    country = "CA"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "['Store #" in line:
            items = line.split("['Store #")
            for item in items:
                if "'map-marker.png'" in item:
                    markers.append(
                        item.split("'")[0]
                        + "|"
                        + item.split(",")[1].strip()
                        + "|"
                        + item.split(",")[2].strip()
                    )
            items = line.split('<h3 class="map__title">')
            for item in items:
                if '</h3><p class="map__content">' in item:
                    name = item.split("<")[0]
                    lat = ""
                    lng = ""
                    store = item.split("#")[1].split("<")[0]
                    for mark in markers:
                        if mark.split("|")[0] == store:
                            lat = mark.split("|")[1]
                            lng = mark.split("|")[2]
                    add = item.split('</h3><p class="map__content">')[1].split("<")[0]
                    zc = "<MISSING>"
                    city = item.split("<br />")[1].split(",")[0]
                    state = item.split("<br />")[1].split(",")[1].split("<")[0].strip()
                    phone = "<MISSING>"
                    hours = "<MISSING>"
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
