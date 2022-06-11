from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rockytopstores_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}

DOMAIN = "https://rockytopstores.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://rockytopstores.com/locations/rocky-top-901"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "changeloc"}).findAll("option")[1:]
        for loc in loclist:
            location_name = loc.text
            store_number = location_name.split("#")[1]
            page_url = "https://rockytopstores.com" + loc["value"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            address = (
                soup.find("span", {"class": "locationaddress"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            temp = address[1].split(",")
            city = temp[0]
            state = temp[1]
            temp = address[2].split()
            zip_postal = temp[-1]
            if "States" in zip_postal:
                zip_postal = MISSING
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
                phone=MISSING,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=MISSING,
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
