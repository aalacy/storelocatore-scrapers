import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("natuzzi_com")


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
    url = "https://www.natuzzi.com/store-locator.html#wrapper_stores"
    r = session.get(url, headers=headers)
    website = "natuzzi.com"
    typ = "<MISSING>"
    loc = "<MISSING>"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'id_store":"' in line:
            items = line.split('id_store":"')
            for item in items:
                if '"title":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"title":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    country = item.split('country":"')[1].split('"')[0]
                    if country == "CA" or country == "US":
                        try:
                            state = (
                                item.split('"geoloc_address":"')[1]
                                .split('"')[0]
                                .replace(", USA", "")
                                .replace(",USA", "")
                                .replace(", Canada", "")
                                .rsplit(",", 1)[1]
                                .strip()
                                .split(" ")[0]
                            )
                        except:
                            state = "<MISSING>"
                    else:
                        state = "<MISSING>"
                    if country == "UK":
                        country = "GB"
                    if " " in state:
                        state = state.split(" ")[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    lat = item.split('"geoloc_lat":"')[1].split('"')[0]
                    lng = item.split('"geoloc_lon":"')[1].split('"')[0]
                    if country == "US" or country == "CA":
                        zc = item.split('"zip":"')[1].split('"')[0]
                        if "FL " in zc:
                            state = "FL"
                            zc = zc.split("FL")[1].strip()
                        if "ON " in zc:
                            state = "ON"
                            zc = zc.split("ON")[1].strip()
                        if phone == "":
                            phone = "<MISSING>"
                        if "Montreal" in city:
                            state = "QC"
                        if "Edmonton" in city:
                            state = "AB"
                        if "Burlington" in city:
                            state = "ON"
                        if "Coquitlam" in city:
                            state = "BC"
                        if "Victoria" in city:
                            state = "BC"
                        if "Winnipeg" in city:
                            state = "MB"
                        if "Greenvile" in city:
                            state = "SC"
                        if "Dallas" in city or "Houston" in city:
                            state = "TX"
                        if "Atlanta" in city:
                            state = "GA"
                        if city == "Bend":
                            state = "OR"
                        if "Las Vegas" in city:
                            state = "NV"
                        if (
                            "Boca Raton" in city
                            or "Fort Lauderdale" in city
                            or "Miami" in city
                        ):
                            state = "FL"
                        if "Los Angeles" in city:
                            state = "CA"
                        if "." not in lat:
                            lat = "<MISSING>"
                            lng = "<MISSING>"
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
