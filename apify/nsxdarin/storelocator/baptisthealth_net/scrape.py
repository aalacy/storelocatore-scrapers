import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("baptisthealth_net")


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
    url = "https://baptisthealth.net/sitemap.xml"
    r = session.get(url, headers=headers)
    bad_urls = [
        "https://baptisthealth.net/Locations/Urgent Care",
        "https://baptisthealth.net/Locations/Surgery Centers",
        "https://baptisthealth.net/Locations/Sleep Centers",
        "https://baptisthealth.net/Locations/Rehabilitation Centers",
        "https://baptisthealth.net/Locations/Primary Care",
        "https://baptisthealth.net/Locations/Physician Practices/Urology",
        "https://baptisthealth.net/Locations/Physician Practices/Orthopedics",
        "https://baptisthealth.net/Locations/Physician Practices/Neuroscience",
        "https://baptisthealth.net/Locations/Physician Practices/General Surgery",
        "https://baptisthealth.net/Locations/Physician Practices/Endocrinology",
        "https://baptisthealth.net/Locations/Physician Practices/Cardiovascular",
        "https://baptisthealth.net/Locations/Physician Practices/Cancer",
        "https://baptisthealth.net/Locations/Physician Practices",
        "https://baptisthealth.net/Locations/Hospitals",
        "ttps://baptisthealth.net/Locations/Endoscopy Centers",
        "https://baptisthealth.net/Locations/Emergency Care",
        "https://baptisthealth.net/Locations/Diagnostic Imaging",
    ]
    website = "baptisthealth.net"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://baptisthealth.net/Locations/" in line:
            items = line.split("<loc>https://baptisthealth.net/Locations/")
            for item in items:
                if "</loc>" in item and " Pricing<" not in item:
                    lurl = "https://baptisthealth.net/Locations/" + item.split("<")[0]
                    if lurl not in bad_urls:
                        locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        typ = loc.split("https://baptisthealth.net/Locations/")[1].split("/")[0]
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"name": "' in line2 and name == "":
                name = line2.split('"name": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if "day:" in line2 and "Hours Today" not in line2:
                days = line2.split("<br/>")
                for day in days:
                    day = day.replace("\t", "").strip()
                    if hours == "":
                        hours = day
                    else:
                        hours = hours + "; " + day
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
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
