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
                    zc = ""
                    store = item.split("#")[1].split("<")[0]
                    for mark in markers:
                        if mark.split("|")[0] == store:
                            lat = mark.split("|")[1]
                            lng = mark.split("|")[2]
                    add = item.split('</h3><p class="map__content">')[1].split("<")[0]
                    city = item.split("<br />")[1].split(",")[0]
                    state = item.split("<br />")[1].split(",")[1].split("<")[0].strip()
                    phone = "807-343-4466"
                    hours = ""
                    loc = (
                        "https://ginospizza.ca/locations/"
                        + city.lower().replace(" ", "+")
                        + "/"
                        + store
                    )
                    r2 = session.get(loc, headers=headers)
                    logger.info(loc)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if '<dt class="list--description__term">' in line2:
                            days = line2.split('<dt class="list--description__term">')
                            for day in days:
                                if '<dd class="list--description__data">' in day:
                                    hrs = (
                                        day.split("<")[0].strip()
                                        + " "
                                        + day.split(
                                            '<dd class="list--description__data">'
                                        )[1]
                                        .split("<")[0]
                                        .strip()
                                        .replace("&mdash;", "-")
                                    )
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                        if "maps.google.com/" in line2:
                            zc = (
                                line2.split("maps.google.com/")[1]
                                .split('" target="')[0]
                                .rsplit("%2C", 1)[1]
                                .upper()
                            )
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
