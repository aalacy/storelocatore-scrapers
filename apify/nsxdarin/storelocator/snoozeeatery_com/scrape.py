import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("snoozeeatery_com")


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
    url = "https://www.snoozeeatery.com/wpsl_stores-sitemap.xml"
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://www.snoozeeatery.com/restaurant/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        name = "Snooze Eatery"
        logger.info(("Pulling Location %s..." % loc))
        website = "snoozeeatery.com"
        typ = "Restaurant"
        add = ""
        city = ""
        state = ""
        zc = ""
        hours = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '{"store":"' in line2:
                name = line2.split('{"store":"')[1].split('"')[0]
                add = line2.split('"address":"')[1].split('"')[0]
                try:
                    add = add + " " + line2.split('"address2":"')[1].split('"')[0]
                except:
                    pass
                add = add.strip()
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"lng":"')[1].split('"')[0]
                store = line2.split('"id":')[1].split("}")[0]
            if "Phone:</label>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                phone = g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
            if "PM</option>" in line2:
                hrs = line2.split(">")[1].split("<")[0].replace("&#8211;", "-")
                if hours == "":
                    hours = "Today: " + hrs
                else:
                    hours = hours + "; " + hrs
        country = "US"
        if "denver-international-airport" in loc:
            phone = "303-342-6612"
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
