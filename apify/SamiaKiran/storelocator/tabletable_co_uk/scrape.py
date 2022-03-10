from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tabletable_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.tabletable.co.uk"
MISSING = SgRecord.MISSING


def get_data(soup):
    raw_address = (
        soup.find("address").get_text(separator="|", strip=True).replace("|", " ")
    )
    pa = parse_address_intl(raw_address)

    street_address = pa.street_address_1
    street_address = street_address if street_address else MISSING

    city = pa.city
    city = city.strip() if city else MISSING

    state = pa.state
    state = state.strip() if state else MISSING

    zip_postal = pa.postcode
    zip_postal = zip_postal.strip() if zip_postal else MISSING
    if zip_postal == MISSING:
        zip_postal = raw_address.split()
        zip_postal = zip_postal[-2] + " " + zip_postal[-1]
    phone = soup.select_one("a[href*=tel]").text
    hours_of_operation = (
        soup.findAll("div", {"class": "info-container__details"})[1]
        .get_text(separator="|", strip=True)
        .replace("|", " ")
        .replace("OPENING TIMES", "")
        .replace("Live sport shown here", "")
        .replace("Opening times", "")
    )
    hours_of_operation = hours_of_operation.lower()
    if "facilities" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("facilities")[0]

    return (
        raw_address,
        street_address,
        city,
        state,
        zip_postal,
        phone,
        hours_of_operation,
    )


def fetch_data():
    if True:
        url = "https://www.tabletable.co.uk/en-gb/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "title-text"})
        for loc in loclist:
            country_code = "UK"
            page_url = DOMAIN + loc["href"]
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                location_name = (
                    soup.find("h1", {"class": "title-text"})
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                )
                page_url = DOMAIN + loc["href"]
                log.info(page_url)
                (
                    raw_address,
                    street_address,
                    city,
                    state,
                    zip_postal,
                    phone,
                    hours_of_operation,
                ) = get_data(soup)
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours_of_operation.strip(),
                    raw_address=raw_address,
                )
            except:
                temp_list = soup.findAll("a", {"class": "h3"})
                for temp in temp_list:
                    page_url = DOMAIN + temp["href"]
                    log.info(page_url)
                    r = session.get(page_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    (
                        raw_address,
                        street_address,
                        city,
                        state,
                        zip_postal,
                        phone,
                        hours_of_operation,
                    ) = get_data(soup)
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
                        country_code=country_code,
                        store_number=MISSING,
                        phone=phone.strip(),
                        location_type=MISSING,
                        latitude=MISSING,
                        longitude=MISSING,
                        hours_of_operation=hours_of_operation.strip(),
                        raw_address=raw_address,
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
