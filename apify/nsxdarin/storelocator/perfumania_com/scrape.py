import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("perfumania_com")


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
    url = "https://secure.gotwww.com/gotlocations.com/perfumania/2020/index.php?bypass=y&c=#"
    r = session.get(url, headers=headers)
    website = "perfumania.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "{icon: customIcon}).addTo(map)" in line:
            lat = line.split("([")[1].split(",")[0]
            lng = line.split(",")[1].split("]")[0]
        if "<div class=map_text><strong>" in line:
            name = line.split("<div class=map_text><strong>")[1].split("<")[0]
            add = line.split("</strong><br>")[1].split("<")[0]
            city = line.split("<br>")[2].split(",")[0]
            state = line.split("<br>")[2].split(",")[1].strip().split(" ")[0]
            zc = line.split("<br>")[2].rsplit(" ", 1)[1]
            store = "<MISSING>"
            phone = line.split("phone:")[1].split("<")[0].strip()
            hours = (
                line.split("hours:")[1]
                .split("<")[0]
                .strip()
                .replace("  ", " ")
                .replace("  ", " ")
            )
            if city == "Buford":
                state = "GA"
            if "storename" not in name:
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
