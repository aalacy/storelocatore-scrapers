import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "cookie": "itsu_user_location=US",
}

logger = SgLogSetup().get_logger("itsu_com")


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
    url = "https://www.itsu.com/wp-admin/admin-ajax.php?action=locationList&lat=40.6515758&lng=-73.8485382&blogId=3"
    r = session.get(url, headers=headers)
    website = "itsu.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        name = item["title"].replace("&amp;", "&")
        add = item["address_1"]
        city = item["city"]
        state = item["state"]
        zc = item["postal_code"]
        phone = "<MISSING>"
        lat = item["latitude"]
        lng = item["longitude"]
        hours = "<MISSING>"
        store = "<MISSING>"
        if "closed" in str(item["hours"]):
            hours = "Closed"
        loc = item["single_url"].replace("\\", "")
        if "0" not in hours:
            hours = "<MISSING>"
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
    url = "https://www.itsu.com/location-sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.itsu.com/location/" in line:
            locs.append(line.split(">")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        country = "GB"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0].replace(" - itsu", "")
            if 'data-long="' in line2:
                lng = line2.split('data-long="')[1].split('"')[0]
                lat = line2.split('-lat="')[1].split('"')[0]
            if '"address_1">' in line2:
                add = (
                    line2.split('"address_1">')[1].split("<")[0]
                    + " "
                    + line2.split('"address_2">')[1].split("<")[0].strip()
                )
                city = line2.split('<p id="city">')[1].split("<")[0].strip()
                zc = line2.split('_code">')[1].split("<")[0].strip()
            if "<p>0" in line2:
                phone = line2.split("<p>")[1].split("<")[0]
            if '<li class="">' in line2:
                items = line2.split('<li class="">')
                for item in items:
                    if "day" in item:
                        hrs = item.split("<")[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if "temporarily closed" in line2:
                hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if "0" not in hours:
            hours = "<MISSING>"
        add = add.replace("&#039;", "'").replace("&amp;", "&")
        city = city.replace("&#039;", "'").replace("&amp;", "&")
        name = name.replace("&#039;", "'").replace("&amp;", "&")
        if "coming-soon" not in loc:
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
