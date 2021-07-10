from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl


logger = SgLogSetup().get_logger("datacenters_com")
locator_domain_url = "https://datacenters.com"

session = SgRequests()
MISSING = "<MISSING>"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def get_all_locations_data():
    urls_us_ca_gb_api_endpoint = [
        "https://www.datacenters.com/api/v1/locations?query=united%20states&withProducts=false&showHidden=false&nearby=false&radius=0&bounds=&circleBounds=&polygonPath=&forMap=true",
        "https://www.datacenters.com/api/v1/locations?query=canada&withProducts=false&showHidden=false&nearby=false&radius=0&bounds=&circleBounds=&polygonPath=&forMap=true",
        "https://www.datacenters.com/api/v1/locations?query=united%20kingdom&withProducts=false&showHidden=false&nearby=false&radius=0&bounds=&circleBounds=&polygonPath=&forMap=true",
    ]
    data_all_for_us_ca_gb = []
    for url_us_ca_gb in urls_us_ca_gb_api_endpoint:
        data_json = session.get(url_us_ca_gb, headers=headers).json()
        data = data_json["locations"]
        data_all_for_us_ca_gb.extend(data)
    return data_all_for_us_ca_gb


def fetch_data():
    data_all = get_all_locations_data()
    us_country_code_names = ["United States", "U.S.", "Usa"]
    uk_country_code_names = ["United Kingdom", "UK"]
    ca_country_code_names = ["Canada"]

    for num_store, d in enumerate(data_all):

        # Locator Domain
        locator_domain = locator_domain_url
        logger.info(f"Extracting the data from: {num_store}: \n{d}\n")

        # Page URL
        page_url = d["url"]
        if page_url:
            page_url = f"{locator_domain}{page_url}"
        else:
            page_url = MISSING

        logger.info(f"Page URL: {page_url} ")

        # Location Name if Data Center or Data Centers found in the location name,
        location_name_data_center = "Data Center"

        location_name = d["providerName"]
        if location_name:
            if "Data Center" in location_name:
                location_name = location_name
            elif "Data Centers" in location_name:
                location_name = location_name
            else:
                location_name = f"{location_name} {location_name_data_center}"
        else:
            location_name = MISSING

        logger.info(f"Location Name: {location_name}")

        # Get address
        add = d["fullAddress"]
        logger.info(f"Full Address Raw: \n{add}\n")

        # Parse Raw Address
        address_to_be_parsed = add
        pa = parse_address_intl(address_to_be_parsed)
        logger.info(f"parsed_address: {pa}")

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

        logger.info(f"Street Address: {street_address}")

        # City
        city = pa.city
        city = city if city else MISSING
        logger.info(f"City: {city}")

        # State
        state = pa.state
        state = state if state else MISSING
        logger.info(f"Location Name: {state}")

        # Zip Code
        zip_postal = pa.postcode
        zip_postal = zip_postal if zip_postal else MISSING
        logger.info(f"Zip Code: {zip_postal}")

        # Country Code
        country_code = pa.country
        if country_code:
            if country_code in us_country_code_names:
                country_code = "US"
            elif country_code in uk_country_code_names:
                country_code = "GB"
            elif country_code in ca_country_code_names:
                country_code = "CA"
            else:
                country_code = country_code
        else:
            country_code = MISSING
        logger.info(f"Country Code: {country_code}")

        # Store Number
        store_number = d["id"] if d["id"] else MISSING
        logger.info(f"Store Number: {store_number}")

        # Phone data can be obtained from each store site
        phone = MISSING
        logger.info(f"Telephone: {phone}")

        # Location Type
        location_type = MISSING

        # Latitude
        latitude = d["latitude"] if d["latitude"] else MISSING
        logger.info(f"Latitude: {latitude}")

        # Longitude
        longitude = d["longitude"] if d["longitude"] else MISSING
        logger.info(f"Longitude: {longitude}")

        hours_of_operation = MISSING
        logger.info(f"HOO: {hours_of_operation}")

        # Raw Address
        raw_address = d["fullAddress"] if d["fullAddress"] else MISSING
        logger.info(f"Raw Address: {raw_address}")

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
