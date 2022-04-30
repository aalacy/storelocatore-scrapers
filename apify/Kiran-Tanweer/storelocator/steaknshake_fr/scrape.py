from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "steaknshake_fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://steaknshake.fr/"
MISSING = SgRecord.MISSING


def fetch_data():
    search_url = "https://steaknshake.fr/adresses/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    json_block = soup.findAll("script", {"type": "text/javascript"})
    data = str(json_block[78])
    data = data.split(";jQuery.extend")[0]
    data = data.split("var mapsvg_options =")[1]
    data = json.loads(data)
    data = data["data_db"]["objects"]
    for loc in data:
        title = loc["ville"]
        lat = loc["location"]["lat"]
        lng = loc["location"]["lng"]
        street = loc["adresse1"]
        try:
            city = loc["regions"][0]["title"]
        except KeyError:
            city = MISSING
        state = loc["location"]["address"]["locality"]
        pcode = loc["location"]["address"]["postal_code"]
        country = loc["location"]["address"]["country_short"]
        phone = loc["telephone"]
        hoo = loc["horaires"]
        storeid = loc["id"]

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=search_url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code=country,
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
        SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE})
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
