from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl

MISSING = "<MISSING>"
DOMAIN = "hm.com"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}

logger = SgLogSetup().get_logger("hm_com")


def fetch_data():
    # Your scraper here
    session = SgRequests()
    start_url = "https://api.storelocator.hmgroup.tech/v2/brand/hm/stores/locale/en_US/country/US?_type=json&campaigns=true&departments=true&openinghours=true&maxnumberofstores=1000"

    # US POI
    data = session.get(start_url, headers=headers).json()
    all_poi = data["stores"]

    # CA POI
    ca_url = "https://api.storelocator.hmgroup.tech/v2/brand/hm/stores/locale/en_US/country/CA?_type=json&campaigns=true&departments=true&openinghours=true&maxnumberofstores=1000"
    ca_data = session.get(ca_url, headers=headers).json()
    all_poi += ca_data["stores"]

    for poi in all_poi:
        # Locator Domain
        locator_domain = DOMAIN

        # Page URL
        page_url = MISSING

        # Location Name
        location_name = poi["name"]
        location_name = location_name if location_name else MISSING

        # Street Address
        street_address1 = poi["address"]["streetName1"].strip().rstrip(",")
        street_address2 = poi["address"]["streetName2"].strip().rstrip(",")
        raw_address = ""
        if street_address2:
            raw_address = street_address1 + ", " + street_address2
        else:
            raw_address = street_address1

        street_address_parsed = parse_address_intl(raw_address)
        street_address_parsed = street_address_parsed.street_address_1
        logger.info(f" Parsed Street Address: {street_address_parsed}")

        # sgpostal returned the following incomplete street addresses,
        # These addresses have been replaced by street address 1 or 2 found in the API response data.
        # Suite No. 2320
        # Building G
        # Suite 1200
        # Suite E2
        # x
        # Unit #C095A
        # Unit #C095A
        # Space #1040
        # Unit # 260
        # H&M Space 84

        street_address = ""
        if street_address2:
            street_address = street_address2
        else:
            street_address = street_address_parsed

        if street_address == "Suite No. 2320":
            street_address = street_address_parsed

        if street_address == "Building G":
            street_address = street_address_parsed

        if street_address == "Suite 1200":
            street_address = street_address_parsed

        if street_address == "Suite E2":
            street_address = street_address_parsed

        if street_address == "x":
            street_address = street_address1

        if street_address == "Unit #C095A":
            street_address = street_address1
        if street_address == "Space #1040":
            street_address = street_address1
        if street_address == "Unit # 260":
            street_address = street_address1
        if street_address == "H&M Space 84":
            street_address = street_address1

        street_address = street_address if street_address else MISSING

        # City
        city = poi["city"]
        if not city:
            city = poi.get("address", {}).get("postalAddress")
        city = city if city else MISSING

        # State
        state = poi.get("region", {}).get("name")
        if not state:
            state = poi.get("address", {}).get("state")
        state = state if state else MISSING

        # Zip Code
        zip_code = poi["address"]["postCode"].strip()
        zip_code = zip_code.replace("US", "").strip()
        zip_code = zip_code if zip_code else MISSING

        # Country Code
        country_code = poi["countryCode"].strip()
        country_code = country_code if country_code else MISSING

        # Store Number
        store_number = poi["storeCode"].strip()
        store_number = store_number if store_number else MISSING

        # Phone Number
        phone = poi.get("phone")
        phone = phone.strip() if phone else MISSING

        # Location Type
        location_type = MISSING
        location_type = location_type if location_type else MISSING

        # Latitude
        latitude = poi["latitude"]
        latitude = latitude if latitude else MISSING

        # Longitude
        longitude = poi["longitude"]
        longitude = longitude if longitude else MISSING

        # Hours of operation
        hours_of_operation = []
        for elem in poi["openingHours"]:
            hours_of_operation.append(
                "{} {} - {}".format(elem["name"], elem["opens"], elem["closes"])
            )
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else MISSING
        )

        # Raw Address
        raw_address = raw_address if raw_address else MISSING

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
