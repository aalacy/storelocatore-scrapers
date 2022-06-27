from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "naturalgrocers_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.naturalgrocers.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        for link in range(50):
            url = (
                "https://www.naturalgrocers.com/store-directory?field_store_address_administrative_area=All&page="
                + str(link)
            )
            log.info(f"Page No {link}")
            main_r = session.get(url, headers=headers, timeout=180)
            soup = BeautifulSoup(main_r.text, "html.parser")
            loclist = soup.findAll(
                "article",
                {"class": "node node--type-store node--view-mode-search-list-card"},
            )[1:]
            for loc in loclist:
                page_url = "https://www.naturalgrocers.com" + loc["about"]
                log.info(page_url)
                location_name = (
                    loc.find("h3").get_text(separator="|", strip=True).replace("|", "")
                )
                if "Coming Soon!" in location_name:
                    continue
                street_address = loc.find("span", {"class": "address-line1"}).text
                city = loc.find("span", {"class": "locality"}).text
                state = loc.find("span", {"class": "administrative-area"}).text
                zip_postal = loc.find("span", {"class": "postal-code"}).text
                country_code = loc.find("span", {"class": "country"}).text
                phone = (
                    loc.find("div", {"class": "store_telephone_number"})
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                )
                hours_of_operation = (
                    loc.find("div", {"class": "office-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                coords = loc.find("div", {"class": "geolocation"})
                latitude = coords["data-lat"]
                longitude = coords["data-lng"]
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
                )
            if "Last page" not in main_r.text:
                break


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
