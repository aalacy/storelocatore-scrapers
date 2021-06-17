from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from lxml import html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("bankofutah_com")
MISSING = "<MISSING>"
DOMAIN = "https://bankofutah.com"
LOCATION_URL = "https://bankofutah.com/locations"

headers = {
    "Content-Type": "application/json",
    "Host": "bankofutah.com",
    "Origin": "https://bankofutah.com",
    "Referer": "https://bankofutah.com/locations",
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

session = SgRequests()


def get_page_urls():
    r = session.get(LOCATION_URL, headers=headers)
    d = html.fromstring(r.text, "lxml")
    urls = d.xpath('//option[contains(@value, "/locations")]/@value')
    urls = [f"{DOMAIN}{i}" for i in urls]
    return urls


def fetch_data():
    page_urls = get_page_urls()
    for idx, url in enumerate(page_urls):
        locator_domain = DOMAIN
        page_url = url
        logger.info(f"Pulling the data from {page_url} ")
        r1 = session.get(url, headers=headers)
        d1 = html.fromstring(r1.text, "lxml")
        location_name = d1.xpath('//h1[@class="hero-title"]/text()')
        location_name = "".join(location_name)
        location_name = location_name if location_name else MISSING
        logger.info(f"Location Name: {location_name}")
        address = d1.xpath(
            '//h4[contains(text(), "Address")]/following-sibling::*[1][self::div]/text()'
        )
        address = "".join(address)
        address = " ".join(address.split())
        logger.info(f"Location Name: {address}")
        address1 = address.split(",")
        street_address = MISSING
        if len(address1) > 3:
            street_address = address1[0] + "," + address1[1]
            street_address = street_address.strip()
        elif len(address1) == 3:
            street_address = address1[0]
            street_address = street_address.strip()
        else:
            street_address = MISSING

        city = address1[-2]
        if city:
            city = city.strip()
        else:
            city = MISSING

        state = address1[-1].strip().split(" ")[0]
        if state:
            state = state.strip()
        else:
            state = MISSING

        zip_postal = address1[-1].split(" ")[-1]
        logger.info(f"Address: {street_address} | {city} | {state} | {zip_postal}")
        country_code = "US"
        store_number = MISSING
        phone = d1.xpath('//div[span[contains(text(), "Main")]]/a/text()')
        phone = "".join(phone)
        if phone:
            phone = phone.strip()
        else:
            phone = MISSING
        logger.info(f"Phone: {phone}")

        # Location Type
        location_type = MISSING

        # Latitude and Longitude
        latlng_url = d1.xpath('//a[@class="get-directions"]/@href')[0]
        logger.info(f"Pulling latlng data from: {latlng_url}")

        headers_g = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        }
        r2 = session.get(latlng_url, headers=headers_g)
        d2 = html.fromstring(r2.text, "lxml")
        latlng_gurl = d2.xpath('//meta[@itemprop="image"]/@content')[0]
        logger.info(f"Latlng Google URL: {latlng_gurl} ")
        latlng = latlng_gurl.split("center=")[-1].split("&zoom")[0]
        latitude = latlng.split("%2C")[0]
        latitude = latitude if latitude else MISSING
        longitude = latlng.split("%2C")[1]
        longitude = longitude if longitude else MISSING
        logger.info(f"Latitude: {latitude} | Longitude: {longitude}")

        # Hours of Operation
        hoo = d1.xpath(
            '//h4[contains(text(), "Lobby Hours") or contains(text(), "Lobby and Drive Thru Hours")]/following-sibling::*[1][self::div]//text()'
        )

        hoo = "".join(hoo)
        if hoo:
            hours_of_operation = hoo.strip()
        else:
            hours_of_operation = MISSING
        logger.info(f"Hours of operation: {hours_of_operation}")

        # Raw Address
        raw_address = address if address else MISSING
        yield SgRecord(
            locator_domain=locator_domain,
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
            raw_address=raw_address,
        )


def scrape():
    logger.info(" Scraping Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
