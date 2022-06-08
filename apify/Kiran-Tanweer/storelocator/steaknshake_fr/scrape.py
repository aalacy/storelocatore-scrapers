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
    data = str(json_block[len(json_block) - 1])
    data = data.split(";jQuery.extend")[0]
    data = data.split("var mapsvg_options =")[1]
    data = json.loads(data)
    data = data["data_db"]["objects"]
    for loc in data:
        title = loc["ville"]
        city = title
        lat = loc["location"]["lat"]
        lng = loc["location"]["lng"]
        phone = loc["telephone"].strip()
        if phone == "":
            phone = MISSING
        store_num = loc["id"]
        country = loc["location"]["address"]["country_short"]
        street = loc["adresse1"]
        if street == "":
            street = loc["location"]["address"]["formatted"].split(",")[0]
        else:
            street = MISSING
        if str(loc).find("administrative_area_level_1") != -1:
            state = loc["location"]["address"]["administrative_area_level_1"]
        else:
            state = MISSING
        if str(loc).find("postal_code") != -1:
            pcode = loc["location"]["address"]["postal_code"]
        else:
            pcode = loc["adresse2"].split(" ")[0]
        hours = loc["horaires"]
        hours = hours.replace("\n", " ").strip()
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=search_url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code=country,
            store_number=store_num,
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
