from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl


DOMAIN = "gpminvestments.com/lilcricket"
logger = SgLogSetup().get_logger("gpminvestments_com__lilcricket")
MISSING = SgRecord.MISSING
INACCESSIBLE = "<INACCESSIBLE>"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}


def fetch_data():
    with SgRequests() as session:
        API_ENDPOINT_URL = "https://gpminvestments.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMo9R0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABk8WwA"
        data_list_json = session.get(API_ENDPOINT_URL, headers=headers).json()
        data_markers = data_list_json["markers"]
        for idx, item in enumerate(data_markers[0:]):
            # Location Domain
            locator_domain = DOMAIN

            # Page URL
            page_url = MISSING

            # Location Name
            location_name = item["title"]
            location_name = " ".join(location_name.split())
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] Location Name: {location_name}")

            # Parse Raw Address
            address_to_be_parsed = item["address"]
            logger.info(f"[{idx}] Address being parsed: {address_to_be_parsed}")

            address_to_be_parsed = address_to_be_parsed.replace(" -", "-")
            pa = parse_address_intl(address_to_be_parsed)

            # Street Address
            street_address_1 = pa.street_address_1
            street_address_2 = pa.street_address_2
            street_address = ""
            if street_address_1 and street_address_2:
                street_address = street_address_1 + " " + street_address_2
            elif street_address_1 and street_address_2 is None:
                street_address = street_address_1
            elif street_address_1 is None and street_address_2 is not None:
                street_address = street_address_2
            else:
                street_address = MISSING

            if street_address == "3630":
                street_address = street_address.replace("3630", "3630 Greenbush")

            # City
            city = pa.city
            city = city if city else MISSING

            # State
            state = pa.state
            state = state if state else MISSING

            # Zip Code
            zipcode = pa.postcode
            zipcode = zipcode if zipcode else INACCESSIBLE

            # Country Code
            country_code = "US"

            # Store Number
            store_number = item["id"]
            store_number = store_number if store_number else MISSING

            # Phone Data
            phone = MISSING

            # Location Type
            location_type = MISSING

            # Latitude
            latitude = ""
            lat = item["lat"]
            if lat == str(0):
                latitude = MISSING
            else:
                if lat:
                    latitude = lat
                else:
                    latitude = MISSING

            # Longitude
            longitude = ""
            lng = item["lng"]
            if lng == str(0):
                longitude = MISSING
            else:
                if lng:
                    longitude = lng
                else:
                    longitude = MISSING

            # Hours of Operation
            hours_of_operation = MISSING

            # Raw Address
            raw_address = item["address"] if item["address"] else MISSING
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
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
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
