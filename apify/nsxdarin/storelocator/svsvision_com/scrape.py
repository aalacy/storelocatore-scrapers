import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("svsvision_com")


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
    url = "https://www.svsvision.com/contact/?state=all"
    r = session.get(url, headers=headers)
    website = "svsvision.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if '<div class="span4"><address><strong>' in line:
            name = line.split('<div class="span4"><address><strong>')[1].split("<")[0]
            add = line.split("</strong><br>")[1].split("<")[0]
            city = name
            state = line.split("<br>")[2].split(" ")[0]
            zc = line.split("<br>")[2].rsplit(" ", 1)[1]
            phone = line.split("<br><br>")[1].split("<")[0]
            try:
                lat = line.split("/@")[1].split(",")[0]
                lng = line.split("/@")[1].split(",")[1]
            except:
                lat = "<MISSING>"
                lng = "<MISSING>"
            hours = line.split('<div class="span3">')[1].split("<")[0]
            HFound = True
            while HFound:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "</div>" in g:
                    HFound = False
                if HFound:
                    hours = hours + "; " + g.split("<")[0]
            hours = hours.replace("day Closed", "day: Closed")
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
