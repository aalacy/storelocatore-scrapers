import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

logger = SgLogSetup().get_logger("novanthealth_org")


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
    ids = []
    url = "https://www.novanthealth.org/DesktopModules/NHLocationFinder/API/Location/ByType"
    payload = {
        "LocationGroupId": "1",
        "Latitude": "",
        "Longitude": "",
        "Distance": "5",
        "SubTypes": "",
        "Keyword": "",
        "SortOrder": "",
        "MaxLocations": "2500",
        "MapBounds": "",
    }
    r = session.post(url, headers=headers, data=payload)
    website = "novanthealth.org"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"Id":' in line:
            items = line.split('{"Id":')
            for item in items:
                if '"StoreCode":"' in item:
                    name = item.split('"BusinessName":"')[1].split('"')[0]
                    store = item.split('"StoreCode":"')[1].split('"')[0]
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    try:
                        loc = item.split('"WebsiteUrl":"')[1].split('"')[0]
                    except:
                        loc = "<MISSING>"
                    add = item.split('"AddressLine":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    state = item.split('"State":"')[1].split('"')[0]
                    try:
                        zc = item.split('"PostalCode":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    typ = "<MISSING>"
                    try:
                        phone = item.split('"PrimaryPhone":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    hours = (
                        item.split('"Display":{')[1]
                        .split("}")[0]
                        .replace('"', "")
                        .replace(",", "; ")
                    )
                    if "Breast Imaging Center" in name and "Greensboro" in name:
                        loc = "https://www.novanthealthimaging.com/locations/greensboro/greensboro-breast-center/"
                    if hours == "":
                        hours = "<MISSING>"
                    addinfo = name
                    if addinfo not in ids:
                        ids.append(addinfo)
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
