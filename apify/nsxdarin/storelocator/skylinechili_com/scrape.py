import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("skylinechili_com")


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
    url = "https://locations.skylinechili.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://locations.skylinechili.com/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    website = "skylinechili.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for loc in locs:
        hours = ""
        phone = ""
        store = loc.split("-chili-")[1]
        r2 = session.get(loc, headers=headers)
        logger.info(loc)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<p class="lp-param lp-param-uHK83o8zrV-paragraph paragraph">' in line2:
                name = (
                    "Skyline Chili "
                    + line2.split(
                        '<p class="lp-param lp-param-uHK83o8zrV-paragraph paragraph">'
                    )[1].split("<")[0]
                )
            if '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
            if '"telephone":"' in line:
                phone = line.split('"telephone":"')[1].split('"')[0].replace("+", "")
            if '{"@type":"OpeningHoursSpecification"' in line2:
                days = line2.split('{"@type":"OpeningHoursSpecification"')
                for day in days:
                    if '"dayOfWeek":"' in day:
                        try:
                            hrs = (
                                day.split('"dayOfWeek":"')[1].split('"')[0]
                                + ": "
                                + day.split('"opens":"')[1].split('"')[0]
                                + "-"
                                + day.split('"closes":"')[1].split('"')[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                        except:
                            pass
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
