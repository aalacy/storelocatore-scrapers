from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "lunardis_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.lunardis.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.lunardis.com/locations"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        divlist = soup.find(
            "div", {"data-mesh-id": "ContainercdeixinlineContent-gridContainer"}
        ).findAll("div", {"data-testid": "richTextElement"})
        for div in divlist:
            if "Phone" not in div.text:
                continue
            div = div.get_text(separator="|", strip=True).split("|")
            if "Peet's Coffee" in div[-1]:
                del div[-1]
            elif "OPEN LONGER TO SERVE YOU" in div[-1]:
                del div[-1]
            location_name = div[0]
            log.info(location_name)
            hours_of_operation = div[-1].replace("Hours:", "")
            phone = div[-2].replace("Store Phone:", "").replace("Meat Dept:", "")
            street_address = " ".join(div[1:-2])
            if "Store Phone:" in street_address:
                street_address = street_address.split("Store Phone:")[0]
            city = location_name
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=search_url,
                location_name=location_name,
                street_address=street_address,
                city=city.strip(),
                state=MISSING,
                zip_postal=MISSING,
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
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
