from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


session = SgRequests()
website = "kia_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.kia.ca"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.kia.ca/en/shopping-tools/find-a-dealer"
    start_url = "https://www.kia.ca/content/marketing/ca/en/shopping-tools/find-a-dealer/jcr:content/root/container/container/section_container_1235319178/find_a_dealer.dealership.json?_postalCode={}"
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=50
    )
    for code in all_codes:
        log.info(f"{code} | remaining: {all_codes.items_remaining()}")
        all_locations = session.get(
            start_url.format(code.replace(" ", "")), headers=headers
        )
        if all_locations.status_code != 200:
            continue
        all_locations = all_locations.json()
        for poi in all_locations:
            location_name = poi["dealership"]["name"]
            log.info(location_name)
            street_address = f"{poi['dealership']['dealershipAddress']['streetNumber']} {poi['dealership']['dealershipAddress']['street']}"
            city = poi["dealership"]["dealershipAddress"]["city"]
            state = poi["dealership"]["dealershipAddress"]["province"]
            zip_postal = poi["dealership"]["dealershipAddress"]["postalCode"]
            country_code = poi["dealership"]["dealershipAddress"].get("country")
            store_number = poi["dealership"]["code"]
            phone = poi["dealership"]["phone"]
            latitude = poi["dealership"]["latitude"]
            longitude = poi["dealership"]["longitude"]
            mon = f"Monday {poi['dealership']['openingHours']['mondayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['mondayClose'].split(':00.000')[0]}"
            tue = f"Tuesday {poi['dealership']['openingHours']['tuesdayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['tuesdayClose'].split(':00.000')[0]}"
            wed = f"Wednesday {poi['dealership']['openingHours']['wednesdayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['wednesdayClose'].split(':00.000')[0]}"
            thu = f"Thursday {poi['dealership']['openingHours']['thursdayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['thursdayClose'].split(':00.000')[0]}"
            if poi["dealership"]["openingHours"].get("fridayOpen"):
                fri = f"Friday {poi['dealership']['openingHours']['fridayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['fridayClose'].split(':00.000')[0]}"
            else:
                fri = ""
            if poi["dealership"]["openingHours"].get("saturdayOpen"):
                sat = f"Saturdayb {poi['dealership']['openingHours']['saturdayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['saturdayClose'].split(':00.000')[0]}"
            else:
                sat = ""
            hours_of_operation = f"{mon} {tue} {wed} {thu}, {fri} {sat}".strip()
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
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
