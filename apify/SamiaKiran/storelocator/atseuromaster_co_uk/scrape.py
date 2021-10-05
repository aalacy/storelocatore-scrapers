from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "therange_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.atseuromaster.co.uk/consumer"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://centre.atseuromaster.co.uk/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        citylist = soup.findAll(
            "div", {"class": "lf-footer-static__content__cities__list__wrapper"}
        )[-1].findAll("a")
        for city in citylist:
            city = city.get_text(separator="|", strip=True).replace("|", " ")
            url = "https://centre.atseuromaster.co.uk/search?query=" + city
            log.info(f"Fetching Locations from {city}")
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("a", {"title": "View centre details"})
            for loc in loclist:
                page_url = "https://centre.atseuromaster.co.uk" + loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = (
                    soup.find("h1")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                latitude = soup.find("meta", {"property": "place:location:latitude"})[
                    "content"
                ]
                longitude = soup.find("meta", {"property": "place:location:longitude"})[
                    "content"
                ]
                raw_address = (
                    soup.find("address")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                phone = soup.find("a", {"class": "lf-location-phone-default__phone"})[
                    "href"
                ].replace("tel:", "")
                hours_of_operation = (
                    soup.find("div", {"id": "lf-openinghours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Show more Hide", "")
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
                country_code = "UK"
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
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
