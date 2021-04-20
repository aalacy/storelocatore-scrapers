from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl
from lxml import html
import json


session = SgRequests()

locator_domain_url = "https://gpminvestments.com/nextdoor"
MISSING = "<MISSING>"
INACCESSIBLE = "<INACCESSIBLE>"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}


logger = SgLogSetup().get_logger("gpminvestments_com__nextdoor")


def fetch_data():
    base_url = "https://gpminvestments.com/store-locator"
    r1 = session.get(base_url, headers=headers)
    datar1 = html.fromstring(r1.text, "lxml")
    data_raw = datar1.xpath(
        '//script[@type="text/javascript" and contains(., "wpgmaps_localize")]/text()'
    )
    data_raw = "".join(data_raw)
    data_json_raw = data_raw.split("wpgmaps_localize_marker_data = ")[-1].split(";")[0]
    data_json = json.loads(data_json_raw)
    for k, v in data_json["7"].items():
        # Location Domain
        locator_domain = locator_domain_url

        # Page URL
        page_url = MISSING

        # Location Name
        location_name = v["title"]
        logger.info(f"Store Number>{k} : {v['address']}")

        # Parse Raw Address
        address_to_be_parsed = v["address"]
        address_to_be_parsed = address_to_be_parsed.replace(" -", "-")
        pa = parse_address_intl(address_to_be_parsed)

        # Street Address
        street_address_1 = pa.street_address_1
        street_address_2 = pa.street_address_2
        street_address = ""
        if street_address_1 and street_address_2:
            street_address = street_address_1 + " " + street_address_2
        elif street_address_1:
            street_address = street_address_1
        else:
            street_address = MISSING

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
        store_number = k if k else MISSING

        # Phone Data
        phone = MISSING

        # Location Type
        location_type = MISSING

        # Latitude
        latitude = ""
        lat = v["lat"]
        if lat == str(0):
            latitude = MISSING
        else:
            if lat:
                latitude = lat
            else:
                latitude = MISSING

        # Longitude
        longitude = ""
        lng = v["lng"]
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
        raw_address = v["address"] if v["address"] else MISSING
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
