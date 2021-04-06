import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from lxml import etree
from tenacity import retry, stop_after_attempt

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger(
    "skyscanner_com__airports__uk__airports-in-united-kingdom"
)

URLS = [
    "https://www.skyscanner.com/airports/uk/airports-in-united-kingdom.html",
    "https://www.skyscanner.com/airports/engla/airports-in-england.html",
    "https://www.skyscanner.com/airports/n_ire/airports-in-northern-ireland.html",
    "https://www.skyscanner.com/airports/scotl/airports-in-scotland.html",
    "https://www.skyscanner.com/airports/wales/airports-in-wales.html",
]

XPATHS = [
    "//div[@id='airports_in_city_frame']//div[@class='lhs_info']//a[contains(@href, '/airports')]/@href",
    "//div[@id='sm_airports_in_country' or @id='sm_airports_in_region' or @id='airports_in_city_frame']//div[@id='airports_in_frame']//a[contains(@href, '/airports')]/@href",
]


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
                "raw_address",
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


def fetch_links(urls):
    unique_links = set()
    for url in urls:
        session = SgRequests()
        response = session.get(url, headers=headers)
        parsed = etree.HTML(response.text)
        for xpath in XPATHS:
            airport_links = parsed.xpath(xpath)
            full_links = [f"https://www.skyscanner.com{link}" for link in airport_links]
            for link in full_links:
                if link.endswith("airports.html"):
                    unique_links |= fetch_links([link])
                elif link.endswith("united-kingdom.html"):
                    continue
                else:
                    unique_links.add(link)
    return unique_links


def or_missing(x):
    assert len(x) <= 1
    if len(x) == 0:
        return "<MISSING>"
    else:
        return str(x[0])


@retry(stop=stop_after_attempt(7))
def get_loc(loc):
    logger.info(loc)
    session = SgRequests()
    response = session.get(loc, headers=headers)
    parsed = etree.HTML(response.text)
    name = or_missing(parsed.xpath("//div[@id='detailsbox']//h6/text()"))
    address_lines = parsed.xpath(
        "//div[@id='detailsbox']//div[@class='content']/p/text()"
    )
    raw_address = ""
    for line in address_lines:
        if "UNITED KINGDOM" in line:
            break
        raw_address += line
    raw_address = raw_address.strip(",")
    addr = parse_address_intl(raw_address)
    city = addr.city
    state = "<MISSING>"
    zc = addr.postcode
    add = addr.street_address_1
    if add is None:
        add = name
    store = or_missing(
        parsed.xpath("//tr[th[contains(text(), 'IATA code:')]]/td/text()")
    )
    phone = or_missing(parsed.xpath("//td[@itemprop='telephone']/text()"))
    lat = or_missing(parsed.xpath("//meta[@itemprop='latitude']/text()"))
    lng = or_missing(parsed.xpath("//meta[@itemprop='longitude']/text()"))
    hours = "<MISSING>"
    website = "https://www.skyscanner.com/airports/uk/airports-in-united-kingdom.html"
    country = "GB"
    typ = "<MISSING>"
    return [
        website,
        loc,
        name,
        raw_address,
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


def fetch_data():
    locs = fetch_links(URLS)
    logger.info(f"found {len(locs)} airport URLs")
    for loc in locs:
        yield get_loc(loc)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
