from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

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
        divlist = soup.findAll("div", {"class": "_1ozXL"})
        for div in divlist:
            details = div.text
            details = details.split("\n")
            hours = details[-1]
            if hours.find("Hours") != -1:
                hoo = details[-1]
                phone = details[-2]
            else:
                hoo = details[-2]
                phone = details[-3]
                if phone.find("Store Phone:") == -1:
                    phone = details[-4]
            hoo = hoo.lstrip("Hours: Open Daily ").strip()
            hoo = hoo.replace("PEN DAILY ", "").strip()
            hoo = "Mon - Sat: " + hoo
            phone = phone.lstrip("Store Phone:").strip()
            title = div.find("span", {"style": "letter-spacing:0.1em;"}).text.strip()
            city = title
            info = div.findAll("div", {"class": "_2Hij5"})[2].text
            street = info.replace("\n", " ").split("Store Phone:")[0].strip()

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=search_url,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=MISSING,
                zip_postal=MISSING,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hoo.strip(),
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
