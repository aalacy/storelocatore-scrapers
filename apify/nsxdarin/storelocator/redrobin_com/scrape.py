import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("redrobin_com")

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
    url = "https://www.redrobin.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://redrobin.com/locations/" in line:
            items = line.split("<loc>https://redrobin.com/locations/")
            for item in items:
                if "</loc>" in item:
                    lurl = "https://redrobin.com/locations/" + item.split("<")[0]
                    if (
                        lurl.count("/") == 6
                        and lurl != "https://redrobin.com/locations/"
                    ):
                        locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        country = "US"
        website = "redrobin.com"
        typ = "Restaurant"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("-", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"location_name\\":\\"' in line2:
                name = line2.split('"location_name\\":\\"')[1].split("\\")[0]
                add = line2.split('\\"address_1\\":\\"')[1].split("\\")[0]
                city = line2.split('\\"city\\":\\"')[1].split("\\")[0]
                state = line2.split('"region\\":\\"')[1].split("\\")[0]
                zc = line2.split('"post_code\\":\\"')[1].split("\\")[0]
                phone = line2.split('"local_phone\\":\\"')[1].split("\\")[0]
                lat = line2.split('"lat\\":\\"')[1].split("\\")[0]
                lng = line2.split('"lng\\":\\"')[1].split("\\")[0]
            if '{"label":"Primary Hours"' in line2:
                days = (
                    line2.split('{"label":"Primary Hours",')[1]
                    .split("]},")[0]
                    .split('"days":{"')[1]
                    .split('{"open":"')
                )
                try:
                    hours = (
                        "Sun: "
                        + days[1].split('"')[0]
                        + "-"
                        + days[1].split('"close":"')[1].split('"')[0]
                    )
                except:
                    hours = "Sun: Closed"
                try:
                    hours = (
                        hours
                        + "; Mon: "
                        + days[2].split('"')[0]
                        + "-"
                        + days[2].split('"close":"')[1].split('"')[0]
                    )
                except:
                    hours = hours + "; Mon: Closed"
                try:
                    hours = (
                        hours
                        + "; Tue: "
                        + days[3].split('"')[0]
                        + "-"
                        + days[3].split('"close":"')[1].split('"')[0]
                    )
                except:
                    hours = hours + "; Tue: Closed"
                try:
                    hours = (
                        hours
                        + "; Wed: "
                        + days[4].split('"')[0]
                        + "-"
                        + days[4].split('"close":"')[1].split('"')[0]
                    )
                except:
                    hours = hours + "; Wed: Closed"
                try:
                    hours = (
                        hours
                        + "; Thu: "
                        + days[5].split('"')[0]
                        + "-"
                        + days[5].split('"close":"')[1].split('"')[0]
                    )
                except:
                    hours = hours + "; Thu: Closed"
                try:
                    hours = (
                        hours
                        + "; Fri: "
                        + days[6].split('"')[0]
                        + "-"
                        + days[6].split('"close":"')[1].split('"')[0]
                    )
                except:
                    hours = hours + "; Fri: Closed"
                try:
                    hours = (
                        hours
                        + "; Sat: "
                        + days[7].split('"')[0]
                        + "-"
                        + days[7].split('"close":"')[1].split('"')[0]
                    )
                except:
                    hours = hours + "; Sat: Closed"
        if add != "":
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
