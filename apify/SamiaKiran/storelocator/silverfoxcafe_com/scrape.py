from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "silverfoxcafe_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://silverfoxcafe.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.silverfoxcafe.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div", {"class": "vc_col-md-4 wpb_column vc_column_container"}
        )
        for loc in loclist:
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text
            hours_of_operation = (
                soup.findAll("div", {"class": "wpb_wrapper"})[9]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("HOURS ", "")
            )
            if hours_of_operation == "HOURS":
                hours_of_operation = MISSING
            temp = soup.find("div", {"class": "address"})
            latitude, longitude = temp.find("a")["href"].rsplit("/")[-1].split(",")
            address = temp.get_text(separator="|", strip=True).split("|")
            if len(address) == 1:
                phone = address[0]
                street_address = MISSING
                city = location_name
                state = MISSING
                zip_postal = MISSING
                country_code = MISSING
            else:
                phone = address[-1]
                street_address = address[1]
                address = address[2].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
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
