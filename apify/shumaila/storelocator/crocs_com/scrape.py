from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "crocs_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.crocs.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://locations.crocs.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"data-group": "1"})
        for loc in loclist:
            page_url = "https://locations.crocs.com" + loc["href"]
            log.info(page_url)
            location_name = "Crocs"
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                temp = (
                    soup.find(
                        "div",
                        {
                            "class": "section-subtitle landing-header-address landing-header-detail-section"
                        },
                    )
                    .get_text(separator="|", strip=True)
                    .split("|")
                )
            except:
                continue
            store_number = soup.find("div", {"id": "retailer-page-wrapper"})["data-id"]
            phone = temp[-1]
            street_address = temp[0]
            address = temp[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            if zip_postal.isnumeric() is False:
                continue
            latitude = r.text.split('"latitude":"')[1].split('"')[0]
            longitude = r.text.split('"longitude":"')[1].split('"')[0]
            hours_of_operation = (
                soup.find("div", {"class": "store-hours-days"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
