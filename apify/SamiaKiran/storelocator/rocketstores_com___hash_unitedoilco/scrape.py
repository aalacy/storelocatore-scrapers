from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rocketstores_com___hash_unitedoilco"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://rocketstores.com/#unitedoilco"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://rocketstores.com/wp-json/stations/v1/locations?MinLong=-119.7746143203125&MaxLong=-116.2040576796875&MinLat=31.831881035524546&MaxLat=35.5152839154545"
        temp = session.get(url, headers=headers).json()
        United_Oil_id = temp["brands"][-1]["term_id"]
        loclist = temp["stations"]
        for loc in loclist:
            if loc["brand"]["term_id"] == United_Oil_id:
                location_name = loc["store_name"]
                log.info(location_name)
                store_number = loc["ID"]
                phone = loc["phone_number"]
                try:
                    street_address = loc["address"] + " " + loc["address2"]
                except:
                    street_address = loc["address"]
                city = loc["city"]
                state = loc["state"]
                zip_postal = loc["zip"]
                country_code = loc["country"]
                latitude = loc["latitude"]
                longitude = loc["longitude"]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://rocketstores.com/rocket-stations/",
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
                    hours_of_operation=MISSING,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
