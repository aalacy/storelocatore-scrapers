import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("adidas_co_uk")


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
    url = "https://www.adidas.co.uk/glass/sitemaps/adidas/GB/en/sitemaps/store-pages-sitemap.xml"
    session = SgRequests()
    r = session.get(url, headers=headers)
    website = "adidas.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>www.adidas.co.uk/storefront/GB" in line:
            locs.append("https://" + line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        if "-online-" not in loc:
            logger.info(loc)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = loc.split("/storefront/")[1].split("-")[0]
            phone = ""
            lat = ""
            lng = ""
            hours = ""
            session = SgRequests()
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if "><h3>" in line2:
                    name = line2.split("><h3>")[1].split("<")[0]
                if '"storeLocator\\":{\\"content\\"' in line2:
                    info = line2.split('"storeLocator\\":{\\"content\\"')[1]
                    add = info.split('"street\\":\\"')[1].split("\\")[0]
                    city = info.split('"city\\":\\"')[1].split("\\")[0]
                    zc = info.split('"postcode\\":\\"')[1].split("\\")[0]
                    state = "<MISSING>"
                    lat = info.split('\\"lat\\":')[1].split(",")[0]
                    lng = info.split('"lng\\":')[1].split("}")[0]
                if '<a title="Phone" href="tel:' in line2:
                    phone = line2.split('<a title="Phone" href="tel:')[1].split('"')[0]
                if '<li class="timerow' in line2:
                    items = line2.split('<li class="timerow')
                    for item in items:
                        if "day</span>" in item:
                            hrs = (
                                item.split("<span>")[1].split("<")[0]
                                + ": "
                                + item.split("day</span><span>")[1].split("<")[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
            if phone == "undefined":
                phone = "<MISSING>"
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
