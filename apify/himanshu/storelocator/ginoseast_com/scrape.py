from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "ginoseast_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.ginoseast.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.ginoseast.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("h3")
        for loc in loclist:
            page_url = DOMAIN + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text
            hours_of_operation = r.text.split(">Hours")[1].split("</div>")[0]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = (
                hours_of_operation.get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Now Open For Safe Indoor Dining Service", "")
                .replace("NOW OPEN FOR DINE IN!", "")
                .replace("Delivery available after 5pm", "")
            )
            if "Reserve" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Reserve")[0]
            phone = r.text.split('">Phone')[1].split("</p>")[0]
            phone = BeautifulSoup(phone, "html.parser").text
            address = r.text.split("Address")[1].split("</p>")[0]
            address = (
                BeautifulSoup(address, "html.parser")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            try:
                zip_postal = address[1]
            except:
                zip_postal = MISSING
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
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
