from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgpostal.sgpostal import parse_address_usa
import json
from lxml import html

DOMAIN = "paintedtree.com"
LOCATION_URL = "https://paintedtree.com/all-locations/"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    HEADERS["Referer"] = url
    r = session.get(url, headers=HEADERS)
    return r


def fetch_data():
    log.info("Fetching store_locator data")
    r = pull_content(LOCATION_URL)
    soup = bs(r.content, "lxml")
    sel = html.fromstring(r.text, "lxml")

    contents = soup.select(
        "section div.elementor-section-wrap div.elementor-container.elementor-column-gap-default"
    )
    coords = json.loads(soup.select_one("div.jet-map-listing")["data-markers"])
    num = 0
    for row in contents:
        coming_soon = row.find("div", {"class": "elementor-ribbon-inner"})
        if coming_soon and "Coming Soon!" in coming_soon.text.strip():
            continue
        page_url = row.find("div", {"data-pafe-section-link": True})[
            "data-pafe-section-link"
        ]
        r1 = pull_content(page_url)
        soup1 = bs(r1.content, "lxml")
        store = soup1.select(
            "div.elementor-column.elementor-col-50.elementor-top-column.elementor-element"
        )[1]
        location_name = row.find("h2", {"class": "elementor-cta__title"}).text.strip()
        raw_address = row.find("div", {"class": "elementor-cta__description"}).get_text(
            strip=True, separator=","
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = store.select_one(
            "div.elementor-hidden-mobile a.elementor-button-link"
        ).text.strip()
        country_code = "US"
        store_number = MISSING
        hours_of_operation = ""
        hoo = sel.xpath(
            '//p[contains(@class, "elementor-heading-title") and contains(text(), "Open Daily")]/text()'
        )
        hoo = "".join(hoo)
        hours_of_operation = hoo or ""
        latitude = coords[num]["latLang"]["lat"]
        longitude = coords[num]["latLang"]["lng"]
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )
        num += 1


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
