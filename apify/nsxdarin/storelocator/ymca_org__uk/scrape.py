import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ymca_org__uk")


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
                "raw_address",
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
    url = "https://www.ymca.org.uk/find-your-local-ymca"
    r = session.get(url, headers=headers)
    website = "ymca.org/uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"slug":"ymcas"' in line:
            items = line.split('"pinColor":""},{"title":"')
            for item in items:
                item = item.replace(
                    'var maplistScriptParamsKo = {"KOObject":[{"id":0,"locations":[{"title":"',
                    "",
                )
                name = item.split('"')[0]
                loc = item.split('"locationUrl":"')[1].split('"')[0].replace("\\", "")
                addinfo = (
                    item.split("<div class='address'><p>")[1]
                    .split("<\\/p>\\n<\\/div>")[0]
                    .replace("\\u00a0", " ")
                )
                addinfo = (
                    addinfo.split("<br \\/>", 1)[1]
                    .replace("\\n", "")
                    .replace("<br \\/>", " ")
                    .replace("  ", " ")
                )
                if "<div class='address'><p>" in item:
                    addinfo = item.split("<div class='address'><p>")[1].split("<\\/p>")[
                        0
                    ]
                    addinfo = (
                        addinfo.replace("<br \\/>", " ")
                        .replace("\\n", "")
                        .replace("  ", " ")
                    )
                try:
                    phone = item.split("Phone: <\\/span>")[1].split("<")[0].strip()
                except:
                    phone = "<MISSING>"
                lat = item.split('"latitude":"')[1].split('"')[0]
                lng = item.split('"longitude":"')[1].split('"')[0]
                addr = parse_address_intl(addinfo)
                city = addr.city
                zc = addr.postcode
                add = addr.street_address_1
                state = "<MISSING>"
                hours = "<MISSING>"
                store = "<MISSING>"
                if loc == "":
                    loc = "<MISSING>"
                if add == "" or add is None:
                    add = "<MISSING>"
                if city == "" or city is None:
                    city = "<MISSING>"
                if zc == "" or zc is None:
                    zc = "<MISSING>"
                name = name.replace("\\u2013", "-")
                add = add.replace("\\u2013", "-")
                if " - part" in name:
                    name = name.split(" - part")[0]
                if "abervalley-ymca" in loc:
                    name = "Abervalley YMCA"
                name = name.replace("\\/", "/")
                add = add.replace("\\/", "/")
                city = city.replace("\\/", "/")
                zc = zc.replace("\\U00A0", " ").replace("\\u00a0", " ")
                yield [
                    website,
                    loc,
                    name,
                    addinfo,
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
