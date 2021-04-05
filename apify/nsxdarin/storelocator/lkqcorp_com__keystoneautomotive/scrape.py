import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("lkqcorp_com__keystoneautomotive")


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
    website = "lkqcorp.com"
    typ = "<MISSING>"
    canada = [
        "QC",
        "ON",
        "NS",
        "NF",
        "NL",
        "PE",
        "PEI",
        "AB",
        "SK",
        "YT",
        "NU",
        "BC",
    ]
    for x in range(1, 240):
        url = (
            "https://www.lkqcorp.com/wp-json/cf-elementor-modules/v1/location-finder/search?category_id=0&lat=&lng=&page="
            + str(x)
            + "&range=0&per_page=8"
        )
        r = session.get(url, headers=headers)
        logger.info("Pulling Stores Page %s..." % str(x))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"post_id":"' in line:
                items = line.split('{"post_id":"')
                for item in items:
                    if "https:" in item:
                        hours = "<MISSING>"
                        lurl = (
                            item.split('"location_url":"')[1]
                            .split('"')[0]
                            .replace("\\", "")
                        )
                        store = item.split('"')[0]
                        lat = item.split('"location_latitude":"')[1].split('"')[0]
                        lng = item.split('"location_longitude":"')[1].split('"')[0]
                        name = item.split('"location_name":"')[1].split('"')[0]
                        phone = item.split('"location_phone":"')[1].split('"')[0]
                        if phone == "":
                            phone = "<MISSING>"
                        addinfo = item.split('"location_address":"')[1].split('"')[0]
                        try:
                            if addinfo.count(",") == 2:
                                add = addinfo.split(",")[0]
                                city = addinfo.split(",")[1].strip()
                                state = addinfo.split(",")[2].strip().split(" ")[0]
                                zc = addinfo.split(",")[2].strip().split(" ", 1)[1]
                            else:
                                add = (
                                    addinfo.split(",")[0]
                                    + " "
                                    + addinfo.split(",")[1].strip()
                                )
                                city = addinfo.split(",")[2].strip()
                                state = addinfo.split(",")[3].strip().split(" ")[0]
                                zc = addinfo.split(",")[3].strip().split(" ", 1)[1]
                        except:
                            name = "none"
                        if (
                            "LKQ" in name[:3]
                            and "Ireland" not in state
                            and "Northern" not in state
                        ):
                            if state in canada:
                                country = "CA"
                            else:
                                country = "US"
                            if "keystone" in name.lower():
                                yield [
                                    website,
                                    lurl,
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
