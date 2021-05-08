from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from lxml import html
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("marriott_com")
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "upgrade-insecure-requests": "1",
}

DOMAIN = "https://www.marriott.com"
MISSING = "<MISSING>"
session = SgRequests()


def fetch_data():
    output_list = []
    url = "https://pacsys.marriott.com/data/marriott_properties_MC_en-US.json"
    response = session.get(url, headers=headers, timeout=180)
    logger.info("JSON data being loaded...")
    response_text = response.text
    store_list = json.loads(response_text)
    data_8 = store_list["regions"]
    for i in data_8:
        for j in i["region_countries"]:
            for k in j["country_states"]:
                for h in k["state_cities"]:
                    for g in h["city_properties"]:
                        locator_domain = DOMAIN
                        key = g["marsha_code"]
                        if key:
                            page_url = (
                                f"{'https://www.marriott.com/hotels/travel/'}{str(key)}"
                            )
                        else:
                            page_url = MISSING
                        logger.info(f"[Page URL: {page_url} ]")

                        # Location Name
                        location_name = g["name"]
                        location_name = location_name if location_name else MISSING

                        # Street Address
                        street_address = g["address"]
                        street_address = street_address if street_address else MISSING

                        # City
                        city = g["city"]
                        city = city if city else MISSING

                        # State
                        state = g["state_name"]
                        state = state if state else MISSING

                        # Zip Code
                        zipcode = g["postal_code"]
                        zip_postal = zipcode if zipcode else MISSING

                        # Country Code
                        country_code = g["country_name"]
                        country_code = country_code if country_code else MISSING

                        # Store Number
                        store_number = MISSING

                        # Phone
                        phone = g["phone"]
                        phone = phone if phone else MISSING

                        # Location Type
                        location_type = "Marriott Hotel"
                        location_type = location_type

                        # Latitude
                        latitude = g["latitude"]
                        latitude = latitude if latitude else MISSING

                        # Longitude
                        longitude = g["longitude"]
                        longitude = longitude if longitude else longitude

                        # Number of Operations

                        hours_of_operation = ""
                        hours_of_operation = (
                            hours_of_operation if hours_of_operation else MISSING
                        )

                        # Raw Address
                        raw_address = ""
                        raw_address = raw_address if raw_address else MISSING

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
