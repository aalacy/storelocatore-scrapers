from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


logger = SgLogSetup().get_logger(logger_name="afdc_energy_gov__stations")
headers = {
    "Content-Type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}

DOMAIN = "https://afdc.energy.gov/"
MISSING = "<MISSING>"
session = SgRequests()


def fetch_data():
    API_KEY = "iev5dbMSYw7xEuFdoN5bGrwj2rVa0bwej24u3Pvc"
    # For All countries
    COUNTRY = "all"

    # Electric Charging Stations Code Name
    FUEL_TYPE = "ELEC"

    # Number of stations returned
    LIMIT_RESULTS = "all"
    url_api = f"https://developer.nrel.gov/api/alt-fuel-stations/v1.json?fuel_type={FUEL_TYPE}&country={COUNTRY}&limit={LIMIT_RESULTS}&api_key={API_KEY}"
    all_data_elec = session.get(url_api, headers=headers, timeout=180).json()
    page_url_format_part = "https://afdc.energy.gov/stations/#/station/"
    for poi in all_data_elec["fuel_stations"]:
        locator_domain = DOMAIN
        if poi["id"]:
            page_url = f"{page_url_format_part}{poi['id']}"
        else:
            page_url = MISSING

        location_name = poi["station_name"]
        if location_name:
            location_name = f"{location_name} {'Charging Station'}"
        else:
            location_name = MISSING

        street_address = poi["street_address"]
        city = poi["city"]
        city = city if city else MISSING

        state = poi["state"]
        zip_postal = poi["zip"]
        country_code = poi["country"]

        store_number = poi["id"]
        store_number = store_number if store_number else MISSING

        phone = poi["station_phone"]
        phone = phone if phone else MISSING

        location_type = poi["access_code"]
        location_type = location_type if location_type else MISSING
        if "private" in location_type:
            continue

        latitude = poi["latitude"]
        latitude = latitude if latitude else MISSING

        longitude = poi["longitude"]
        longitude = longitude if longitude else MISSING

        hours_of_operation = poi["access_days_time"]
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING

        raw_address = ""
        raw_address += street_address
        raw_address += ", " + state
        raw_address += " " + zip_postal
        raw_address += ", " + country_code
        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
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
