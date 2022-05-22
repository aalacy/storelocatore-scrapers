from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "zios_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://zios.com"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://zios.com/locations/?disp=all"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "loc-panel"})
    for div in divlist:
        det = div.findAll("li", {"class": "col-md-6"})
        for dt in det:
            temp = dt.get_text(separator="|", strip=True).split("|")
            location_name = temp[0].replace("(Currently being remodeled.)", "")
            if "(Currently being remodeled.)" in temp[0]:
                hours_of_operation = MISSING
                phone = MISSING
                street_address = temp[2]
                address = temp[3].split(",")[1].split()
                city = location_name
                state = address[0]
                zip_postal = address[1]
            else:
                hours_of_operation = dt.text.split("Store Hours")[1].split(
                    "Catering Information"
                )[0]
                street_address = temp[1]
                address = temp[2].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
                phone = temp[3].replace("Phone:", "")
            log.info(street_address)
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
