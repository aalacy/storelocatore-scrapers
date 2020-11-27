import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bestwestern_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_session():
    return SgRequests().requests_retry_session(retries=0, backoff_factor=0)


session = get_session()


def get(url, headers, attempts=1):
    global session
    if attempts == 10:
        raise SystemExit(f"Could not get {url} after {attempts} attempts.")
    try:
        logger.info(f"Attempting GET: {url}")
        r = session.get(url, headers=headers, timeout=10)
        logger.info(f"Got status {r.status_code} for {url}")
        r.raise_for_status()
        return r
    except Exception as e:
        logger.info(e)
        logger.info("restarting session and trying again")
        session = get_session()
        return get(url, headers, attempts + 1)


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
    url = "https://www.bestwestern.com/etc/seo/bestwestern/hotels.xml"
    r = get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if (
            "<loc>https://www.bestwestern.com/en_US/book/" in line
            and "https://www.bestwestern.com/en_US/book/hotels-in-" not in line
        ):
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)
    logger.info(("Found %s Locations..." % str(len(locs))))
    for loc in locs:
        website = "bestwestern.com"
        typ = "<MISSING>"
        hours = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = ""
        store = loc.split("/propertyCode.")[1].split(".")[0]
        phone = ""
        lat = ""
        lng = ""

        r2 = get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"

        for line2 in r2.iter_lines(decode_unicode=True):
            if "&#34;street1&#34;:&#34;" in line2:
                add = line2.split("&#34;street1&#34;:&#34;")[1].split("&#34")[0]
                city = line2.split("&#34;city&#34;:&#34;")[1].split("&#34")[0]
                state = line2.split("&#34;state&#34;:&#34;")[1].split("&#34")[0]
                country = line2.split("&#34;country&#34;:&#34;")[1].split("&#34")[0]
                zc = line2.split("&#34;postalcode&#34;:&#34;")[1].split("&#34")[0]
                phone = line2.split("&#34;phoneNumber&#34;:&#34;")[1].split("&#34")[0]
                lat = line2.split("&#34;,&#34;latitude&#34;:&#34;")[1].split("&#34")[0]
                lng = line2.split("&#34;longitude&#34;:&#34;")[1].split("&#34")[0]
                name = (
                    line2.split("&#34;name&#34;:&#34;")[1]
                    .split("&#34")[0]
                    .replace("\\u0026", "&")
                )
                if "United States" in country:
                    country = "US"
                if "Canada" in country:
                    country = "CA"
                if country == "US":
                    zc = zc[:5]
        if country == "US" or country == "CA":
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
