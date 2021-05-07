import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("theburgerspriest_com")


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
    url = "https://theburgerspriest.com/find-a-location/"
    r = session.get(url, headers=headers)
    website = "theburgerspriest.com"
    typ = "<MISSING>"
    name = "The Burger's Priest"
    country = "CA"
    store = "<MISSING>"
    hours = ""
    lat = "<MISSING>"
    lng = "<MISSING>"
    loc = "<MISSING>"
    zc = "<MISSING>"
    day = ""
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ", AB<" in line or ", ON<" in line:
            day = ""
            hours = ""
            if ", AB<" in line:
                state = "AB"
                city = line.split(", AB<")[0].rsplit(">", 1)[1].strip()
                add = line.split(", AB<")[0].rsplit("<br", 1)[0].rsplit(">", 1)[1]
            else:
                state = "ON"
                city = line.split(", ON<")[0].rsplit(">", 1)[1].strip()
                add = line.split(", ON<")[0].rsplit("<br", 1)[0].rsplit(">", 1)[1]
        if '<a href="tel:' in line:
            phone = line.split('<a href="tel:')[1].split(">")[1].split("<")[0].strip()
        if 'e-list-title">' in line and " Eve<" not in line and " Day<" not in line:
            day = line.split('e-list-title">')[1].split("<")[0]
        if 'lementor-price-list-price">' in line and day != "":
            hrs = (
                day + ": " + line.split('lementor-price-list-price">')[1].split("<")[0]
            )
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
        if "</a></li>" in line and "<" not in line.replace("</a></li>", ""):
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
    hours = "<MISSING>"
    city = "Oakville"
    state = "ON"
    add = "487 Cornwall Rd"
    phone = "(905) 338-5527"
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
    city = "Ottawa"
    add = "1677 Bank St"
    state = "ON"
    phone = "(613) 260-7828"
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
