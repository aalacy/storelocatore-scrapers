import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("shopplanetblue_com")


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
    url = "https://shopplanetblue.com/pages/find-a-store"
    r = session.get(url, headers=headers)
    website = "shopplanetblue.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    phone = ""
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if "<h5>" in line:
            name = line.split("<h5>")[1].split("<")[0]
            add1 = next(lines)
            add1 = (
                str(add1.decode("utf-8"))
                .split('class="store-card__excerpt">')[1]
                .split("<")[0]
            )
            g = next(lines)
            g = (
                str(g.decode("utf-8"))
                .replace("\r", "")
                .replace("\t", "")
                .replace("\n", "")
                .replace("<p>", "")
                .replace("</p>", "")
            )
            h = next(lines)
            h = (
                str(h.decode("utf-8"))
                .replace("\r", "")
                .replace("\t", "")
                .replace("\n", "")
                .replace("<p>", "")
                .replace("</p>", "")
            )
            i = next(lines)
            i = (
                str(i.decode("utf-8"))
                .replace("\r", "")
                .replace("\t", "")
                .replace("\n", "")
                .replace("<p>", "")
                .replace("</p>", "")
            )
            j = next(lines)
            j = (
                str(j.decode("utf-8"))
                .replace("\r", "")
                .replace("\t", "")
                .replace("\n", "")
                .replace("<p>", "")
                .replace("</p>", "")
            )
            if ") " in h:
                add = ""
                city = g.split(",")[0]
                state = g.split(",")[1].strip().split(" ")[0]
                zc = g.rsplit(" ", 1)[1]
                phone = h
            if ") " in j:
                add = g + " " + h
                city = i.split(",")[0]
                state = i.split(",")[1].strip().split(" ")[0]
                zc = i.rsplit(" ", 1)[1]
                phone = j
            if ") " in i:
                add = g
                city = h.split(",")[0]
                state = h.split(",")[1].strip().split(" ")[0]
                zc = h.rsplit(" ", 1)[1]
                phone = i
            if len(add1) >= 2:
                add = add1 + " " + add
        if (
            '<div class="content-grid__item"' in line
            or '<div id="shopify-section-footer"' in line
        ):
            if phone != "":
                hours = "Temporarily Closed"
                phone = phone.replace("<span>", "").replace("</span>", "")
                add = add.replace("<span>", "").replace("</span>", "")
                state = state.replace("<span>", "").replace("</span>", "")
                zc = zc.replace("<span>", "").replace("</span>", "")
                city = city.replace("<span>", "").replace("</span>", "")
                if "Soho" in name:
                    add = "191 Lafayette St"
                add = add.replace('<span itemprop="streetAddress">', "")
                city = city.replace('<span itemprop="streetAddress">', "")
                state = state.replace('<span itemprop="streetAddress">', "")
                phone = phone.replace('<span itemprop="streetAddress">', "")
                add = add.replace("Scottsdale Quarter", "").strip()
                add = add.replace("West Village", "").strip()
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
