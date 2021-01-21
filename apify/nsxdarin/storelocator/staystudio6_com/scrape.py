import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("staystudio6_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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


@retry(stop=stop_after_attempt(3))
def get_url(lurl):
    session = SgRequests()
    r = session.get(lurl, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    return r.json()


def fetch_data():
    locs = []
    ids = []
    url = "https://www.motel6.com/content/g6-cache/property-summary.1.json"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '"property_id":"' in line:
            items = line.split('"property_id":"')
            for item in items:
                if 'lastCreatedOrUpdated":"' not in item:
                    locs.append(item.split('"')[0])
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "staystudio6.com"
        purl = "https://www.motel6.com/en/motels." + loc + ".html?ncr=true"
        typ = ""
        hours = "<MISSING>"
        lurl = "https://www.motel6.com/bin/g6/propertydata." + loc + ".json?lng=en"
        array = get_url(lurl) 
        lat = array["latitude"]
        lng = array["longitude"]
        typ = array["brand_id"]
        add = array["address"]["address_line_0"]
        zc = array["zip"]
        city = array["city"]
        name = array["name"]
        state = array["state"]
        country = array["country"]
        phone = array["phone"]
        store = array["property_id"]
        addinfo = add + city + state
        if addinfo not in ids:
            ids.append(addinfo)
            yield [
                website,
                purl,
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
