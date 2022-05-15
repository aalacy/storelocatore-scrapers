from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "levinfurniture_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://levinfurniture.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.levinfurniture.com/store/locator"
        r = session.get(url, headers=headers)
        key = r.text.split("https://api.blueport.com/v1/session/region?key=")[1].split(
            "&"
        )[0]
        api_url = (
            "https://api.blueport.com/v1/store/postalcode?key="
            + key
            + "&postalCode=10001&distance.distance=9999&distance.unit=Miles"
        )
        loclist = session.get(api_url, headers=headers).json()["stores"]
        for loc in loclist:
            location_name = loc["storeName"]
            if "LEVIN ONLINE" in location_name:
                continue
            store_number = loc["storeKey"]
            address = loc["storeAddress"]
            phone = address["telephone"]
            street_address = address["thoroughfare"]
            city = address["locality"]
            state = address["administrativeArea"]
            zip_postal = address["postalCode"]
            country_code = address["country"]
            try:
                page_url = "https://www.levinfurniture.com/store" + loc["storeUrl"]
            except:
                page_url = MISSING
            hour_list = loc["storeHours"]
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation + " " + hour["day"] + " " + hour["storeHours"]
                )
            log.info(page_url)
            latitude = loc["latitude"]
            longitude = loc["longitude"]
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
