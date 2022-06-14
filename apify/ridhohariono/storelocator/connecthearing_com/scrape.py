from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "connecthearing.com"
BASE_URL = "https://clinics.connecthearing.com/"
LOCATION_URL = "https://clinics.connecthearing.com/index.html"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(table):
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-location-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-location-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"class": "Directory-content"})
    state_links = content.find_all("a", {"class": "Teaser-titleLink"})
    for row in state_links:
        store_urls.append(BASE_URL + row["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    for page_url in page_urls:
        soup = pull_content(page_url)
        location_name = handle_missing(
            soup.find("h1", {"id": "location-name"}).get_text(
                strip=True, separator=" | "
            )
        )
        address = soup.find("address", {"id": "address"})
        street_address = address.find("meta", {"itemprop": "streetAddress"})["content"]
        city = handle_missing(
            address.find("meta", {"itemprop": "addressLocality"})["content"]
        )
        state = handle_missing(address.find("abbr", {"itemprop": "addressRegion"}).text)
        zip_postal = handle_missing(
            address.find("span", {"class": "c-address-postal-code"}).text.strip()
        )
        country_code = address["data-country"]
        store_number = "<MISSING>"
        phone = soup.find("span", {"id": "telephone"}).text.strip()
        hours_of_operation = parse_hours(
            soup.find("table", {"class": "c-location-hours-details"})
        )
        location_type = "<MISSING>"
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
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
            raw_address=f"{street_address}, {city}, {state}, {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
