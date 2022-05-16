from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "yesway_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://yesway.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://yesway.com/wp-content/themes/yesway/locations/locations.json"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            store_number = loc["id"]
            loc = loc["acf"]
            location_type = loc["primary_category"]
            location_name = loc["business_name"]
            try:
                phone = loc["primary_phone"].replace(
                    '["325-692-8736"," Press 3"]', "325-692-8736"
                )
            except:
                phone = MISSING
            try:
                street_address = loc["address_line_1"] + " " + loc["address_line_2"]
            except:
                street_address = loc["address_line_1"]
            if "PO Box" in street_address:
                try:
                    street_address = street_address.split(",")[1]
                except:
                    street_address = street_address.split("PO Box")[0]
            street_address = street_address.replace('"', "").replace("]", "")
            log.info(street_address)
            city = loc["city"]
            state = loc["state"]
            try:
                zip_postal = loc["postal_code"]
            except:
                zip_postal = MISSING
            country_code = loc["country"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            try:
                mon = "Mon " + loc["monday"]
            except:
                mon = MISSING
            try:
                tue = " Tue " + loc["tuesday"]
            except:
                tue = MISSING
            try:
                wed = " Wed " + loc["wednesday"]
            except:
                wed = MISSING
            try:
                thu = " thu " + loc["thursday"]
            except:
                thu = MISSING
            try:
                fri = " Fri " + loc["friday"]
            except:
                fri = MISSING
            try:
                sat = " Sat " + loc["saturday"]
            except:
                sat = MISSING
            try:
                sun = " Sun " + loc["sunday"]
            except:
                sun = MISSING
            hours_of_operation = mon + tue + wed + thu + fri + sat + sun
            if "Mon  Tue  Wed  thu  Fri  Sat  Sun" in hours_of_operation:
                hours_of_operation = MISSING
            elif (
                hours_of_operation
                == "<MISSING><MISSING><MISSING><MISSING><MISSING><MISSING><MISSING>"
            ):
                hours_of_operation = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
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
