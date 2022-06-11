from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("suntrust_com")
MISSING = "<MISSING>"
session = SgRequests()
DOMAIN = "https://www.suntrust.com"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "accept": "application/json",
}


def fetch_data():
    s = set()
    start_url = "https://www.mapquestapi.com/search/v2/radius?origin=10002&radius=3000&maxMatches=2000&ambiguities=ignore&hostedData=mqap.32547_SunTrust_Branch_Loc&outFormat=json&key=Gmjtd|lu6zn1ua2d,70=o5-l0850"
    data = session.get(start_url, headers=headers, timeout=180).json()

    for poi in data["searchResults"]:
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
        country_code = "US"

        country_code = country_code if country_code else MISSING
        store_number = poi["fields"]["RecordId"]
        store_number = store_number if store_number else MISSING
        if store_number in s:
            continue
        s.add(store_number)

        phone = poi["fields"]["Phone_Published"]
        phone = phone if phone else MISSING

        # List of location types whether it is branch or atm
        # In order to form page URL, we would need to get
        # the data for location type e.g., branch or atm
        # Note: Mortgage URL does not follow this pattern

        location_type_purl = ""
        if poi["fields"]["Is_Branch"] == 1 and poi["fields"]["Is_ATM"] == 0:
            location_type_purl = "branch"
            logger.info(f"Location Type Branch: {location_type_purl}")
        else:
            if poi["fields"]["Is_Branch"] == 1 and poi["fields"]["Is_ATM"] == 1:
                location_type_purl = "branch"
                logger.info(f"Location Type Branch: {location_type_purl}")
            else:
                if poi["fields"]["Is_Branch"] == 0 and poi["fields"]["Is_ATM"] == 1:
                    location_type_purl = "atm"
                    logger.info(f"Location Type ATM: {location_type_purl}")
                else:
                    if (
                        poi["fields"]["Is_Branch"] is None
                        and poi["fields"]["Is_ATM"] == 1
                    ):
                        location_type_purl = "atm"
                        logger.info(f"Location Type ATM: {location_type_purl}")
                    else:
                        if (
                            poi["fields"]["Is_Branch"] == 1
                            and poi["fields"]["Is_ATM"] is None
                        ):
                            location_type_purl = "branch"
                            logger.info(f"Location Type: {location_type_purl}")
                        else:
                            location_type_purl = MISSING
        list_of_service_types = []
        location_type = ""
        if poi["fields"]["Is_Branch"] == 1:
            list_of_service_types.append("Branch")
        if poi["fields"]["Is_ATM"] == 1:
            list_of_service_types.append("ATM")
        if poi["fields"]["Ic"] == 1:
            list_of_service_types.append("IC")
        if poi["fields"]["Is_Commercial_Center"] == 1:
            list_of_service_types.append("Commercial Center")
        if poi["fields"]["Is_Instore_Branch"] == 1:
            list_of_service_types.append("Instore Branch")
        if poi["fields"]["Is_Investment_Center"] == 1:
            list_of_service_types.append("Investment Center")
        if poi["fields"]["Is_Mortgage_Office"] == 1:
            list_of_service_types.append("Mortgage Office")
        if poi["fields"]["Is_SB_Solutions"] == 1:
            list_of_service_types.append("SB Solutions")
        if poi["fields"]["Is_Teller_Connect"] == 1:
            list_of_service_types.append("Teller Connect")
        if list_of_service_types:
            location_type = ", ".join(list_of_service_types)
        else:
            location_type = MISSING

        logger.info(f"Location Type: {location_type}")
        latitude = poi["fields"]["mqap_geography"]["latLng"]["lat"]
        latitude = latitude if latitude else MISSING
        longitude = poi["fields"]["mqap_geography"]["latLng"]["lng"]
        longitude = longitude if longitude else MISSING
        hours_of_operation = poi["fields"]["Hours_Lobby_For_VRU"]

        if "CLOSED" in hours_of_operation or not hours_of_operation:
            closed_hrs = "Monday {}; Tuesday {}; Wednesday {}; Thursday {}; Friday {}; Saturday-Sunday {}"
            closed_hrs = closed_hrs.format(
                poi["fields"]["branch_hrs_mon_lobby"],
                poi["fields"]["branch_hrs_tue_lobby"],
                poi["fields"]["branch_hrs_wed_lobby"],
                poi["fields"]["branch_hrs_thu_lobby"],
                poi["fields"]["branch_hrs_fri_lobby"],
                poi["fields"]["branch_hrs_wkend_lobby"],
            )
            hours_of_operation = closed_hrs
        if (
            hours_of_operation
            == "Monday ; Tuesday ; Wednesday ; Thursday ; Friday ; Saturday-Sunday "
        ):
            hours_of_operation = MISSING

        if (
            hours_of_operation
            == "Monday CLOSED; Tuesday CLOSED; Wednesday CLOSED; Thursday CLOSED; Friday CLOSED; Saturday-Sunday "
        ):
            hours_of_operation = "Monday CLOSED; Tuesday CLOSED; Wednesday CLOSED; Thursday CLOSED; Friday CLOSED; Saturday-Sunday CLOSED"

        hours_of_operation = hours_of_operation if hours_of_operation else MISSING

        # To build the page URL, seo name has been used, see below
        seo_name = poi["fields"]["seo_name"]
        page_url = MISSING
        if location_type_purl != MISSING:
            page_url = "https://www.suntrust.com/{}/{}/{}/{}/{}"
            page_url = page_url.format(
                location_type_purl,
                state.lower(),
                city.replace(" ", "-").lower(),
                zip_code,
                seo_name,
            )
        logger.info(f"Page URL: {page_url}")
        raw_address = MISSING

        yield SgRecord(
            locator_domain=DOMAIN,
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
