import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("surlatable_com")


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
    url = "https://www.surlatable.com/stores"
    r = session.get(url, headers=headers)
    website = "surlatable.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            '<a class="store-name" href="/store-details?StoreID=' in line
            and "=600" not in line
        ):
            locs.append(
                "https://www.surlatable.com" + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        name = ""
        city = ""
        state = ""
        add = ""
        zc = ""
        phone = ""
        store = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split(">")[1].split("<")[0]
            if '"openingHours":"' in line2:
                hours = line2.split('"openingHours":"')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
            if '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '"addressRegion":"' in line2:
                state = line2.split('"addressRegion":"')[1].split('"')[0]
            if '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if "latitude&quot;:" in line2:
                lat = line2.split("latitude&quot;:")[1].split("&")[0]
                lng = line2.split("longitude&quot;:")[1].split("&")[0]
        store = loc.rsplit("=", 1)[1]
        if ",Holiday" in hours:
            hours = hours.split(",Holiday")[0].strip()
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
