import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger(
    "britainsfinest_co_uk__attractions__search__class__theme-parks-adventure-parks"
)


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
    url = "https://www.britainsfinest.co.uk/attractions/search/class/theme-parks-adventure-parks"
    r = session.get(url, headers=headers)
    website = (
        "britainsfinest.co.uk/attractions/search/class/theme-parks-adventure-parks"
    )
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'itemprop="name" class="text-capitalize">' in line:
            locs.append(
                "https://www.britainsfinest.co.uk"
                + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "Open Times:</strong>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "<br />" in g:
                    hours = g.split("<br />")[0].strip()
            if 'vendorName: "' in line2:
                name = line2.split('vendorName: "')[1].split('"')[0]
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if '<span itemprop="addressRegion" style="display:none">' in line2:
                city = line2.split(
                    '<span itemprop="addressRegion" style="display:none">'
                )[1].split("<")[0]
            if '<span itemprop="postalCode" style="white-space: nowrap;">' in line2:
                zc = line2.split(
                    '<span itemprop="postalCode" style="white-space: nowrap;">'
                )[1].split("<")[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
        name = name.replace("&#39;", "'").replace("&amp;", "&")
        add = add.replace("&#39;", "'").replace("&amp;", "&")
        if "http" in hours:
            hours = "<MISSING>"
        if "Please see" in hours or "Please visit" in hours:
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
