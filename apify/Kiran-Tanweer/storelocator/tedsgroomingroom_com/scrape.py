from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import json


session = SgRequests()
website = "tedsgroomingroom_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.tedsgroomingroom.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.tedsgroomingroom.com/locations"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        soup = soup.find("script", {"type": "text/javascript"})
        soup = str(soup)
        soup = soup.split("var $locations =")[1].strip()
        soup = soup.split("</script>")[0].strip()
        soup = soup.rstrip(";").strip()
        soup = json.loads(soup)
        for store in soup:
            storeid = store["id"]
            title = store["name"]
            phone = store["phone"]
            street1 = store["address_line_1"]
            street2 = store["address_line_2"]
            street = street1 + " " + street2
            city = store["city"]
            pcode = store["postcode"]
            lat = store["latitude"]
            lng = store["longitude"]
            hours = store["extra_json"]["opening_hours"]
            hours = BeautifulSoup(hours, "html.parser")
            hours = hours.findAll("label")
            hoo = ""
            for hour in hours:
                hoo = hoo + " " + hour.text
            slug = store["slug"]
            site = "https://www.tedsgroomingroom.com/locations/" + slug
            state = MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=site,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="UK",
                store_number=storeid,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
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
