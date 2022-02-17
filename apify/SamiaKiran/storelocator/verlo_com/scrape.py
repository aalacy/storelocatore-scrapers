import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "verlo_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://verlo.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://www.verlo.com/find-a-location/"
        log.info("Fetching Item Id ...")
        r = session.get(url, headers=headers)
        Itemid = r.text.split("Itemid=")[1].split('"')[0]
        api_url = (
            "http://code.metalocator.com/index.php?option=com_locator&view=directory&layout=combined&Itemid="
            + Itemid
            + "Itemid+&tmpl=component&framed=1&source=js"
        )
        r = session.get(api_url, headers=headers)
        loclist = r.text.split("var location_data =")[1].split("[]}]")[0]
        loclist = json.loads(loclist + "[]}]")
        for loc in loclist:
            try:
                page_url = "http:" + loc["link"]
            except:
                continue
            location_name = loc["name"]
            log.info(page_url)
            store_number = loc["id"]
            try:
                street_address = loc["address"]
            except:
                continue
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postalcode"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            phone = loc["phone"]
            try:
                hours_of_operation = loc["fields"]["hours"]["meta"]
            except:
                continue
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = hours_of_operation.findAll("meta")
            hours_of_operation = " ".join(x["content"] for x in hours_of_operation)
            if "Sun" not in hours_of_operation:
                hours_of_operation = "Sun closed " + hours_of_operation
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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
