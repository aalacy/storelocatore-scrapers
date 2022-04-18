from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "pizzamann_at"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.pizzamann.at"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        daylist = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday",
        }
        url = "https://www.pizzamann.at/api/filialen"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["short_name"]
            log.info(location_name)
            raw_address = loc["name"]
            store_number = loc["key"]
            phone = MISSING
            latitude = loc["coords"]["position"]["lat"]
            longitude = loc["coords"]["position"]["lng"]
            country_code = "AT"
            hour_list = loc["oeffnungszeiten"]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            if city == MISSING:
                city = location_name.split()[-1]

            hours_of_operation = ""
            for idx, hour in enumerate(hour_list):
                day = daylist[int(hour)]
                time = hour_list[str(hour)]
                time = time["offen_von"] + "-" + time["offen_von"]
                hours_of_operation = hours_of_operation + " " + day + " " + time
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.pizzamann.at/filialen",
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
                raw_address=raw_address,
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
