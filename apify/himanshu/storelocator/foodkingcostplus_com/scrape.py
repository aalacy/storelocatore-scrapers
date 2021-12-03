from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "foodkingcostplus.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    with SgRequests() as session:
        base_url = "https://foodkingcostplus.com"
        r = session.get(base_url + "/contact-us/")
        location_list = json.loads(
            r.text.split("gmpAllMapsInfo = ")[1].split("];")[0] + "]"
        )[0]["markers"]
        for i in range(len(location_list)):
            store_data = location_list[i]
            locator_domain = website
            page_url = "https://foodkingcostplus.com/contact-us/"
            location_name = store_data["title"]
            cleanr = list(
                BeautifulSoup(store_data["description"], "lxml").stripped_strings
            )
            street_address = ""
            city = ""
            state = ""
            zip = ""
            try:
                raw_address = store_data["address"]
                formatted_addr = parser.parse_address_usa(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

            except:
                pass

            if street_address is None:
                street_address = (
                    store_data["description"]
                    .split("<p>")[1]
                    .split("</p>")[0]
                    .split(",")[0]
                    .strip()
                )
            if city is None:
                city = (
                    store_data["description"]
                    .split("<p>")[1]
                    .split("</p>")[0]
                    .split(",")[1]
                    .strip()
                )

            if state is None:
                state = (
                    store_data["description"]
                    .split("<p>")[1]
                    .split("</p>")[0]
                    .split(",")[2]
                    .split(" ")[1]
                    .strip()
                )

            if zip is None:
                zip = (
                    store_data["description"]
                    .split("<p>")[1]
                    .split("</p>")[0]
                    .split(",")[2]
                    .split(" ")[2]
                    .strip()
                )

            country_code = "US"
            store_number = store_data["id"]
            phone = cleanr[-1].split(":")[1].strip()
            location_type = "<MISSING>"
            latitude = store_data["position"]["coord_y"]
            longitude = store_data["position"]["coord_x"]

            hours = ""
            try:
                hours = cleanr[1].split("Hours:")[1].replace("\xa0", "").strip()
            except:
                hours = cleanr[-1].split("Hours:")[1].replace("\xa0", "").strip()
                phone = cleanr[-2].split(":")[1].strip()

            if not hours:
                hours = cleanr[2].replace("\xa0", "").strip()
            hours_of_operation = hours

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
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
