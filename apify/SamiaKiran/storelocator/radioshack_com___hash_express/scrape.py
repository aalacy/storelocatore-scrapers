from bs4 import BeautifulSoup
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "radioshack_com___hash_express"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.radioshack.com/#express"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://cdn.shopify.com/s/files/1/1490/5112/t/71/assets/store_locator_stores_min.json"
        loclist = session.get(url, headers=headers).json()["features"]
        for loc in loclist:
            if "HobbyTown" in loc["properties"]["Name"]:
                coords = loc["geometry"]["coordinates"]
                latitude = coords[1]
                longitude = coords[0]
                loc = loc["properties"]
                location_name = (
                    BeautifulSoup(loc["Name"], "html.parser")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                log.info(location_name)
                phone = loc["Phone"]
                store_number = loc["Store Number"]
                street_address = loc["Address"]
                city = loc["City"]
                state = loc["Province/State"]
                zip_postal = loc["Postal/Zip Code"]
                country_code = loc["Country"]
                hours_of_operation = (
                    str(loc["Hours"]).replace("<br>", " ").replace("\n", " ")
                )
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://www.radioshack.com/pages/store-locator",
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal,
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
