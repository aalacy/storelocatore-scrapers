import re
import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tapasrevolution_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.tapasrevolution.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.tapasrevolution.com/find-us"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text.lower(), "html.parser")
        loclist = soup.findAll("a", string=re.compile("find out more"))
        for loc in loclist:
            page_url = loc["href"]
            if "tapasrevolution" not in page_url:
                page_url = DOMAIN + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.find("section", {"class": "Main-content"})
            try:
                raw_address = str(temp).split("ADDRESS:</h2>")[1].split("</p>")[0]
            except:
                raw_address = str(temp).split("Address:</h2>")[1].split("</p>")[0]
            raw_address = raw_address.split(">")[1]
            temp = temp.get_text(separator="|", strip=True).replace("|", " ").lower()
            location_name = (
                soup.find("h2")
                .text.replace("Now open -", "")
                .replace("Now OPEN -", "")
                .replace("nOW OPEN -", "")
            )
            hours_of_operation = temp.split("opening hours")[1].split("bookings")[0]
            if "we do not" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("we do not")[0]
            if "aperitivo" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("aperitivo")[0]
            hours_of_operation = hours_of_operation.replace(":", "")
            phone = temp.split("phone:")[1].split("e-mail")[0]
            phone = phone.split()
            try:
                phone = phone[0] + " " + phone[1] + " " + phone[2]
            except:
                phone = phone[0]
            temp = soup.find("div", {"class": "map-block"})["data-block-json"]
            temp = json.loads(temp)
            latitude = temp["location"]["markerLat"]
            longitude = temp["location"]["markerLng"]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            street_address = street_address.replace("Tapas Revolution", "").replace(
                city, ""
            )
            country_code = "UK"
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
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
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
