import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("nationwide_co_uk")


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
    url = "https://locations.nationwidebranches.co.uk/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "nationwide.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://locations.nationwidebranches.co.uk/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") >= 4:
                locs.append(lurl.replace("&#39;", "'").replace("&amp;", "&"))
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
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'c-bread-crumbs-name">' in line2:
                name = line2.split('"c-bread-crumbs-name">')[1].split("<")[0]
            if add == "" and 'class="c-address-street-1">' in line2:
                add = line2.split('class="c-address-street-1">')[1].split("<")[0]
                city = line2.split('class="c-address-city">')[1].split("<")[0]
                state = "<MISSING>"
                try:
                    zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                except:
                    zc = "<MISSING>"
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'c-phone-main-number-link" href="tel:' in line2 and phone == "":
                phone = line2.split('c-phone-main-number-link" href="tel:')[1].split(
                    '"'
                )[0]
            if "data-days='[{" in line2 and hours == "":
                days = line2.split("data-days='[{")[1].split("}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        hrs = day.split('"')[0] + ": "
                        if '"intervals":[]' in day:
                            hrs = hrs + "Closed"
                        else:
                            hrs = (
                                hrs
                                + day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
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
