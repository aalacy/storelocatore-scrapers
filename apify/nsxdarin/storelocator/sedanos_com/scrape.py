import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("sedanos_com")


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
    url = "https://sedanos.com/stores/"
    r = session.get(url, headers=headers)
    website = "sedanos.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if 'h4 class="h3">' in line:
            name = line.split('h4 class="h3">')[1].split("<")[0]
            store = ""
            hours = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            phone = ""
            if "#" in name:
                store = name.split("#")[1].strip()
        if '<div class="address">' in line:
            g = next(lines)
            g = str(g.decode("utf-8"))
            g = g.split("<div>")[1].split("</div>")[0].strip()
            g = g.replace("<br>", "")
            g = g.replace(" FL", ", FL").replace(",,", ",")
            if g.count(",") == 3:
                add = g.split(",")[0].strip()
                city = g.split(",")[1].strip()
                state = g.split(",")[2].strip()
                zc = g.split(",")[3].strip()
            else:
                add = g.split(",")[0].strip()
                city = g.split(",")[1].strip()
                state = g.split(",")[2].strip().split(" ")[0]
                zc = g.rsplit(" ", 1)[1]
        if 'aria-label="Phone' in line:
            phone = line.split('aria-label="Phone')[1].split('"')[0].strip()
        if "day" in line or "24 hours" in line:
            hours = line.split('">')[1].split("<")[0].strip().replace("\t", "")
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
