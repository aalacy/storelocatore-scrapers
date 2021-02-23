import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome

logger = SgLogSetup().get_logger("mattressfirm_com")

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
    sms = []
    session = SgRequests()
    url = "https://www.mattressfirm.com/sitemap_index.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        print(line)
        if "sitemap_stores" in line:
            sms.append(line.split(">")[1].split("<")[0])
    for sm in sms:
        r2 = session.get(sm, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if (
                "<loc>https://www.mattressfirm.com/stores/" in line2
                and ".html" in line2
            ):
                lurl = (
                    line2.split("<loc>")[1]
                    .split("<")[0]
                    .replace("https:/w", "https://w")
                )
                if lurl not in locs:
                    locs.append(lurl)
    logger.info(("Found %s Locations..." % str(len(locs))))
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "mattressfirm.com"
        typ = "Mattress Firm"
        hours = ""
        name = ""
        store = loc.rsplit("-", 1)[1].split(".")[0]
        phone = ""
        lat = ""
        lng = ""
        country = "US"
        add = ""
        city = ""
        state = ""
        zc = ""
        with SgChrome() as driver:
            driver.get(url)
            text = driver.page_source
            text = str(text).replace("\r", "").replace("\n", "").replace("\t", "")
            if "Mattress Firm Clearance" in text:
                typ = "Mattress Firm Clearance"
            if name == "" and "<title>" in text:
                name = text.split("<title>")[1].split("<")[0]
                if "|" in name:
                    name = name.split(" |")[0]
            if '"telephone": "' in text:
                phone = text.split('"telephone": "')[1].split('"')[0]
            if '"streetAddress": "' in text:
                add = text.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in text:
                city = text.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in text:
                state = text.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in text:
                zc = text.split('"postalCode": "')[1].split('"')[0]
            if '"openingHours": "' in text:
                hours = text.split('"openingHours": "')[1].split('"')[0]
            if '"latitude": "' in text:
                lat = text.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in text:
                lng = text.split('"longitude": "')[1].split('"')[0]
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
