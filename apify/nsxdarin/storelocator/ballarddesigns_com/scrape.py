import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ballarddesigns_com")


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
    url = "https://www.ballarddesigns.com/BallardDesigns/US/CustomerService/store-locations/content-path"
    r = session.get(url, headers=headers)
    website = "ballarddesigns.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<h3 id="location-title' in line:
            items = line.split('<h3 id="location-title')
            for item in items:
                if 'Store">' in item:
                    locs.append(
                        "https://www.ballarddesigns.com"
                        + item.split('<a href="')[1].split('"')[0]
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        CS = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'page-header hidden-mobile">' in line2:
                name = line2.split('page-header hidden-mobile">')[1].split(
                    " Information"
                )[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0].strip()
                lng = line2.split('"longitude":')[1].split("}")[0].strip()
                city = line2.split('"addressLocality": "')[1].split('"')[0]
                state = line2.split('"addressRegion": "')[1].split('"')[0]
                zc = line2.split('"postalCode": "')[1].split('"')[0]
                add = line2.split('"streetAddress": "')[1].split('"')[0]
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if "coming soon" in line2:
                CS = True
            if "Regular Store Hours:</h5>" in line2:
                try:
                    hours = (
                        line2.split("Regular Store Hours:</h5>")[1]
                        .split("<!-- <p>")[1]
                        .split("</p> -->")[0]
                        .replace("<br />", "; ")
                        .replace("<br>", "; ")
                    )
                except:
                    hours = (
                        line2.split("<!--<p>")[1]
                        .split("</p> -->")[0]
                        .replace("<br />", "; ")
                        .replace("<br>", "; ")
                    )
                hours = (
                    hours.replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("\t", "")
                )
        if "</p></div>" in hours:
            hours = hours.split("</p></div>")[0]
        if phone == "":
            phone = "<MISSING>"
        if CS:
            hours = "Coming Soon"
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
