import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("coltonssteakhouse_com")


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
    url = "http://coltonssteakhouse.com/map.php?loc=all"
    r = session.get(url, headers=headers)
    website = "coltonssteakhouse.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<A href="store_detail.php?id=' in line:
            locs.append(
                "http://coltonssteakhouse.com/store_detail.php?id="
                + line.split('<A href="store_detail.php?id=')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("=", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'vertical-align:middle;">' in line2:
                name = line2.split('vertical-align:middle;">')[1].split("<")[0]
            if 'src="https://maps.google.com/maps?' in line2:
                lat = line2.split("q=")[1].split(",")[0]
                lng = line2.split("q=")[1].split(",")[1].split("&")[0]
            if "<H4>Info:</H4>" in line2:
                add = line2.split("<H4>Info:</H4>")[1].split("<")[0]
                csz = line2.split("<BR>")[1]
                city = csz.split(",")[0]
                zc = csz.rsplit(" ", 1)[1]
                state = csz.split(",")[1].strip().split(" ")[0]
                phone = line2.split("<BR>")[2]
                phone = phone.split(":")[1].strip()
                hours = (
                    line2.split("Store Hours:</H4>")[1]
                    .split("<BR><BR>")[0]
                    .replace("<BR>", "; ")
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
