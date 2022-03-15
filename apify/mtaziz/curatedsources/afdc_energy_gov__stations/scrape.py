from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
import random

logger = SgLogSetup().get_logger(logger_name="afdc_energy_gov__stations")
headers = {
    "Content-Type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}

DOMAIN = "https://afdc.energy.gov/"
MISSING = "<MISSING>"


def fetch_data():
    with SgRequests() as http:
        API_KEY = "iev5dbMSYw7xEuFdoN5bGrwj2rVa0bwej24u3Pvc"
        # For All countries
        COUNTRY = "all"

        # Electric Charging Stations Code Name
        FUEL_TYPE = "ELEC"

        # Number of stations returned
        LIMIT_RESULTS = "all"
        url_api = f"https://developer.nrel.gov/api/alt-fuel-stations/v1.json?fuel_type={FUEL_TYPE}&country={COUNTRY}&limit={LIMIT_RESULTS}&api_key={API_KEY}"
        all_data_elec = http.get(url_api, headers=headers).json()
        time.sleep(random.randint(5, 20))
        page_url_format_part = "https://afdc.energy.gov/stations/#/station/"
        for poi in all_data_elec["fuel_stations"]:
            locator_domain = DOMAIN
            if poi["id"]:
                page_url = f"{page_url_format_part}{poi['id']}"
            else:
                page_url = MISSING

            # Ev Network
            ev_network = poi["ev_network"]
            location_name = poi["station_name"]
            if (
                ev_network is None
                or ev_network == "All"
                or ev_network == "Non-Networked"
            ):
                location_name = f"{location_name} {'Charging Station'}"
            else:
                location_name = ev_network + " " + "Charging Station"

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

            location_type = poi["fuel_type_code"]
            location_type = location_type if location_type else MISSING

            # Drop private stations
            location_type_private_or_public = poi["access_code"]
            if "private" in location_type_private_or_public:
                continue

            latitude = poi["latitude"]
            latitude = latitude if latitude else MISSING

            longitude = poi["longitude"]
            longitude = longitude if longitude else MISSING

            hours_of_operation = poi["access_days_time"]
            hours_of_operation = hours_of_operation if hours_of_operation else MISSING

            raw_address = ""
            try:
                raw_address += street_address
                raw_address += ", " + state
                raw_address += " " + zip_postal
                raw_address += ", " + country_code
            except:
                raw_address = MISSING

            status_code = poi["status_code"]

            # P and T Stand for Planned & Temporarily Unavailable Resepectively )
            if status_code == "P" or status_code == "T":
                continue
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
