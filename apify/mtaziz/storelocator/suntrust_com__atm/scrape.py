from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

logger = SgLogSetup().get_logger("suntrust_com__atm")
MISSING = "<MISSING>"
session = SgRequests()
DOMAIN = "https://www.suntrust.com"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "accept": "application/json",
}


def fetch_data():
    # Your scraper here
    start_url = "https://www.mapquestapi.com/search/v2/radius?origin=10002&radius=3000&maxMatches=2000&ambiguities=ignore&hostedData=mqap.32547_SunTrust_Branch_Loc&outFormat=json&key=Gmjtd|lu6zn1ua2d,70=o5-l0850"
    data = session.get(start_url, headers=headers, timeout=180).json()
    s = set()
    for idx, poi in enumerate(data["searchResults"]):
        location_name = poi["name"]
        location_name = location_name if location_name else MISSING
        street_address = poi["fields"]["address"]
        street_address = street_address if street_address else MISSING
        city = poi["fields"]["city"]
        city = city if city else MISSING
        state = poi["fields"]["state"]
        state = state if state else MISSING
        zip_code = poi["fields"]["postal"]
        zip_code = zip_code if zip_code else MISSING
        country_code = poi["fields"]["country"]
        country_code = country_code if country_code else MISSING
        store_number = poi["fields"]["RecordId"]
        store_number = store_number if store_number else MISSING
        if store_number in s:
            continue
        s.add(store_number)

        phone = poi["fields"]["Phone_Published"]
        phone = phone if phone else MISSING
        location_type = ""
        if poi["fields"]["Is_Branch"] == 1 and poi["fields"]["Is_ATM"] == 0:
            location_type = "branch"
            logger.info(f"Location Type Branch: {location_type}")
        else:
            if poi["fields"]["Is_Branch"] == 1 and poi["fields"]["Is_ATM"] == 1:
                location_type = "branch"
                logger.info(f"Location Type Branch: {location_type}")
            else:
                if poi["fields"]["Is_Branch"] == 0 and poi["fields"]["Is_ATM"] == 1:
                    location_type = "atm"
                    logger.info(f"Location Type ATM: {location_type}")
                else:
                    if (
                        poi["fields"]["Is_Branch"] is None
                        and poi["fields"]["Is_ATM"] == 1
                    ):
                        location_type = "atm"
                        logger.info(f"Location Type ATM: {location_type}")
                    else:
                        if (
                            poi["fields"]["Is_Branch"] == 1
                            and poi["fields"]["Is_ATM"] is None
                        ):
                            location_type = "branch"
                            logger.info(f"Location Type: {location_type}")
                        else:
                            location_type = MISSING
        location_type = location_type if location_type else MISSING
        logger.info(f"Location Type: {location_type}")
        latitude = poi["fields"]["mqap_geography"]["latLng"]["lat"]
        latitude = latitude if latitude else MISSING
        longitude = poi["fields"]["mqap_geography"]["latLng"]["lng"]
        longitude = longitude if longitude else MISSING
        hours_of_operation = poi["fields"]["Hours_Lobby_For_VRU"]
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        seo_name = poi["fields"]["seo_name"]
        store_url = MISSING
        if location_type != MISSING:
            store_url = "https://www.suntrust.com/{}/{}/{}/{}/{}"
            store_url = store_url.format(
                location_type,
                state.lower(),
                city.replace(" ", "-").lower(),
                zip_code,
                seo_name,
            )
        logger.info(f"Pulling the data from : {idx}: {store_url} ")
        raw_address = MISSING
        if MISSING in store_url:
            continue

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=store_url,
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
    logger.info("Scraping Started")
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
