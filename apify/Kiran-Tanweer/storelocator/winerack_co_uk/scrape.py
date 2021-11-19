from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import json


session = SgRequests()
website = "winerack_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "http://winerack.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.winerack.co.uk/store-locator/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        script = soup.find("script")
        script = str(script)
        script = script.rstrip("</script>").strip()
        script = script.rstrip(";").strip()
        script = script.lstrip("<script>").strip()
        script = script.lstrip("var map_locations = ").strip()
        script = json.loads(script)
        for store in script:
            title = store["title"]
            phone = store["telephone"]
            lat = store["latitude"]
            lng = store["longitude"]
            link = store["link"]
            hours = store["openingTimesTable"]
            address = store["storeAddress"]
            address = address.replace("<br>", " ")
            address = address.replace("<br/>", " ")
            hours = hours.replace("<br>", " ")
            hours = hours.replace("<br/>", " ")
            hours = BeautifulSoup(hours, "html.parser")
            address = BeautifulSoup(address, "html.parser")
            address = address.findAll("p")
            hours = hours.text
            if len(address) == 5:
                street = address[0].text + " " + address[1].text
                city = address[2].text
                locality = address[3].text.strip()
            if len(address) == 4:
                street = address[0].text
                city = address[1].text
                locality = address[2].text.strip()
            locality = locality.strip()
            locality = locality.replace(" ", "-")
            loc = locality.split("-")

            if len(loc) == 4:
                pcode = loc[-2] + " " + loc[-1]
                state = loc[1] + " " + loc[0]
            if len(loc) == 3:
                pcode = loc[-2] + " " + loc[-1]
                state = loc[0]
            else:
                state = "<MISSING>"
                pcode = loc[-2] + " " + loc[-1]

            hours = hours.replace("day", "day ").strip()
            hours = hours.replace("pm", "pm ").strip()

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="UK",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
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
