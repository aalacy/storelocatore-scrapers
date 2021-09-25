from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rachellebery_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://rachellebery.ca/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.rachellebery.ca/fr/trouver-un-magasin/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "store-result"})
        for loc in loclist:
            temp = loc.find("h4")
            page_url = temp.find("a")["href"]
            log.info(page_url)
            location_name = temp.get_text(separator="|", strip=True).replace("|", "")
            try:
                street_address = (
                    loc.find("span", {"class": "location_address_address_1"}).text
                    + " "
                    + loc.find("span", {"class": "location_address_address_2"}).text
                )
            except:
                street_address = loc.find(
                    "span", {"class": "location_address_address_1"}
                ).text
            city = loc.find("span", {"class": "city"}).text
            state = loc.find("span", {"class": "province"}).text
            zip_postal = loc.find("span", {"class": "postal_code"}).text
            phone = loc.find("span", {"class": "phone"}).text
            hours_of_operation = (
                str(loc["data-hours"])
                .replace("{", "")
                .replace("}", "")
                .replace(",", " ")
                .replace('":"', " ")
                .replace('"', "")
            )
            latitude = loc["data-lat"]
            longitude = loc["data-lng"]
            country_code = "CA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
                hours_of_operation=hours_of_operation.strip(),
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
