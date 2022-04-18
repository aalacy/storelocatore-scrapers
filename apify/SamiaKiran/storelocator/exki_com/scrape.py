import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "exki_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.exki.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.exki.com/fr/restaurants"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var select_store_locations =")[1].split("}];")[0]
        loclist = json.loads(loclist + "}]")
        for loc in loclist:
            location_type = MISSING
            location_name = strip_accents(loc["name"])
            store_number = loc["id"]
            phone = loc["phone"]
            if "N/A" in phone:
                phone = MISSING
            street_address = strip_accents(loc["address"])
            log.info(location_name)
            city = strip_accents(loc["city"])
            state = strip_accents(loc["state"])
            zip_postal = loc["zip"]
            raw_address = street_address + " " + city + " " + state + zip_postal
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = loc["country"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            if "False" in location_name:
                location_name = MISSING
            if "False" in city:
                city = MISSING
            if "False" in zip_postal:
                zip_postal = MISSING
            if len(location_name) < 3:
                location_name = MISSING
            mon = "Mon " + loc["monday_open"] + loc["monday_close"]
            tue = " Tue " + loc["tuesday_open"] + loc["tuesday_close"]
            wed = " Wed " + loc["wednesday_open"] + loc["wednesday_close"]
            thu = " Thu " + loc["thursday_open"] + loc["thursday_close"]
            fri = " Fri " + loc["friday_open"] + loc["friday_close"]
            sat = " Sat " + loc["saturday_open"] + loc["saturday_close"]
            sun = " Sun " + loc["sunday_open"] + loc["sunday_close"]
            hours_of_operation = mon + tue + wed + thu + fri + sat + sun
            if "Temporarily closed" in hours_of_operation:
                location_type = "Temporarily closed"
                hours_of_operation = MISSING
            elif hours_of_operation == "Mon Tue Wed Thu Fri Sat Sun":
                hours_of_operation = MISSING
            elif hours_of_operation == "Mon  Tue  Wed  Thu  Fri  Sat  Sun":
                hours_of_operation = MISSING
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
                location_type=location_type,
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
