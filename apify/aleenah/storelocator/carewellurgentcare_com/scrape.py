import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "carewellurgentcare_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.carewellurgentcare.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.carewellurgentcare.com/centers/"
        r = session.get(url, headers=headers)
        loclist = (
            r.text.split("var centersJSON = '")[1]
            .split("<div>")[0]
            .split("'</script>")[0]
        )
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = loc["title"]
            store_number = loc["id"]
            phone = MISSING
            page_url = DOMAIN + loc["link"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            phone = soup.select_one("a[href*=tel]").text
            address = (
                BeautifulSoup(loc["address"]["address"], "html.parser")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            latitude = loc["address"]["lat"]
            longitude = loc["address"]["lng"]
            hours_of_operation = (
                soup.find("p", {"class": "hours"})
                .get_text(separator="|", strip=True)
                .split("|")[:-1]
            )
            if len(hours_of_operation) > 2:
                del hours_of_operation[0]
            hours_of_operation = " ".join(hours_of_operation)
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
