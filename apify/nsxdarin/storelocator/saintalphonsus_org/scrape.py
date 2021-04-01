import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("saintalphonsus_org")


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


def fetch_data():
    locs = []
    url = "https://www.saintalphonsus.org/find-a-location/locations-results?LocationDescendants=true&page=1&count=500"
    r = session.get(url, verify=False, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '"DirectUrl\\":\\"' in line:
            items = line.split('"DirectUrl\\":\\"')
            for item in items:
                if 'DynamicPageZones\\":[]}]' not in item:
                    locs.append(
                        "https://www.saintalphonsus.org"
                        + item.split('\\",\\"LocationName')[0]
                    )
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        rs = session.get(loc, headers=headers)
        website = "saintalphonsus.org"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        hours = ""
        country = "US"
        typ = "Office"
        store = ""
        lat = ""
        lng = ""
        for line2 in rs.iter_lines(decode_unicode=True):
            if '"Latitude\\":' in line2:
                store = line2.split('"Id\\\\\\":')[1].split(",")[0]
                lat = line2.split('"Latitude\\\\\\":')[1].split(",")[0]
                lng = line2.split('"Longitude\\\\\\":')[1].split(",")[0]
                city = line2.split('"City\\\\\\":\\\\\\"')[1].split("\\")[0]
                state = line2.split('"StateName\\\\\\":\\\\\\"')[1].split("\\")[0]
                zc = line2.split('PostalCode\\\\\\":\\\\\\"')[1].split("\\")[0]
                phone = line2.split('"Phone\\\\\\":\\\\\\"')[1].split("\\")[0]
                try:
                    hours = (
                        line2.split('"Values\\":[\\"')[1]
                        .split('\\"],')[0]
                        .replace('\\",\\"', "; ")
                    )
                except:
                    hours = ""
                add = line2.split('"Address1\\\\\\":\\\\\\"')[1].split("\\")[0]
                try:
                    add = (
                        add
                        + " "
                        + line2.split('"Address2\\\\\\":\\\\\\"')[1].split("\\")[0]
                    )
                except:
                    pass
                add = add.strip()
            if '"twitter:title" content="' in line2:
                name = line2.split('"twitter:title" content="')[1].split('"')[0]
                name = name.replace(" - Saint Alphonsus", "")
        if "Page Not" not in name:
            if hours == "":
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            name = name.replace("&amp;", "&")
            add = add.replace("&amp;", "&")
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
