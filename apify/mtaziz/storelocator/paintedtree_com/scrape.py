from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
from lxml import html
import time


logger = SgLogSetup().get_logger("paintedtree_com")

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}

DOMAIN = "https://www.paintedtree.com"
base_url = "https://www.paintedtree.com/locations"
MISSING = "<MISSING>"

session = SgRequests()


def get_latlng_and_other_fields():
    items_from_google_map_as_alternative = []
    r = session.get(base_url, headers=headers)
    data_r = html.fromstring(r.text, "lxml")
    xpath_locations = '//p[contains(@class, "font")]//a[contains(@href, "https://www.google.com/maps/place")]/@href'
    data_locations = data_r.xpath(xpath_locations)
    xpath_location_names = '//p[contains(@class, "font")]//a[contains(@href, "https://www.google.com/maps/place")]//text()'
    location_names = data_r.xpath(xpath_location_names)
    logger.info(f"location names: {location_names}")
    logger.info(f"Number of Stores found: {len(location_names)}")

    for idx, data in enumerate(data_locations):
        logger.info(f" Raw Data:\n {data} \n")
        locator_domain = DOMAIN

        # Page URL
        page_url = data

        # Location Name
        location_name = location_names[idx].replace("Coming Soon:", "").strip()
        logger.info(f"location name: {location_name}")

        # Address Data
        if "/@" in data:

            address_data = data.split("https://www.google.com/maps/place/")[-1].split(
                "/@"
            )
            ra = address_data[0].replace("+", " ")
            logger.info(f"Address Data: {address_data}")

            # Street Address
            ra_scp = ra.split(",")
            street_address = ra_scp[0].strip()
            street_address = street_address if street_address else MISSING

            # City
            try:
                city = ra_scp[1].strip()
            except Exception:
                city = MISSING

            # State
            sp = ra_scp[2].strip().split(" ")
            state = sp[0].strip()
            state = state if city else MISSING

            # Zipcode
            zip_postal = sp[1].strip()
            zip_postal = zip_postal if zip_postal else MISSING

            # Country Code
            country_code = "US"

            # Store Number
            store_number = ""
            store_number = store_number if store_number else MISSING

            # Phone
            phone = ""
            phone = phone if phone else MISSING

            # Location Type
            location_type = ""
            location_type = location_type if location_type else MISSING

            # Latitude and Longitude Raw Data

            logger.info(f"LatLng Raw Data: {address_data[1]}")
            latlng = address_data[1].split(",17z")[0]
            logger.info(f"LatLng Raw Data: {latlng}")

            # Latitude
            latitude = latlng.split(",")[0].strip()
            latitude = latitude if latitude else MISSING

            # Longitude
            longitude = latlng.split(",")[1].strip()
            longitude = longitude if longitude else MISSING

            hours_of_operation = MISSING
            raw_address = ra

        else:
            address_data = data.split("https://www.google.com/maps/place/")[-1].split(
                "/data"
            )
            ra = address_data[0].replace("+", " ")
            logger.info(f"Address Data: {address_data}")

            # Street Address
            ra_scp = ra.split(",")
            street_address = ra_scp[0].strip()
            street_address = street_address if street_address else MISSING

            # City
            try:
                city = ra_scp[1].strip()
            except Exception:
                city = MISSING

            # State
            sp = ra_scp[2].strip().split(" ")
            state = sp[0].strip()
            state = state if city else MISSING

            # Zipcode
            zip_postal = sp[1].strip()
            zip_postal = zip_postal if zip_postal else MISSING

            # Country Code
            country_code = "US"

            # Store Number
            store_number = ""
            store_number = store_number if store_number else MISSING

            # Phone
            phone = ""
            phone = phone if phone else MISSING

            # Location Type
            location_type = ""
            location_type = location_type if location_type else MISSING

            # Latitude and Longitude Raw Data
            latitude = MISSING
            longitude = MISSING

            # Hourse of Operation
            hours_of_operation = MISSING
            raw_address = ra

        row_dict = {
            "locator_domain": locator_domain,
            "page_url": page_url,
            "location_name": location_name,
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip_postal": zip_postal,
            "country_code": country_code,
            "store_number": store_number,
            "phone": phone,
            "location_type": location_type,
            "latitude": latitude,
            "longitude": longitude,
            "hours_of_operation": hours_of_operation,
            "raw_address": raw_address,
        }

        items_from_google_map_as_alternative.append(row_dict)
    return items_from_google_map_as_alternative


def fetch_data():
    latlng = get_latlng_and_other_fields()
    logger.info("Pulling the data from iframe")
    with SgChrome(
        is_headless=True,
    ) as driver:
        driver.get(base_url)
        time.sleep(60)
        logger.info("Trying to get the data from SgChrome response")
        iframe = driver.find_element_by_xpath('//iframe[@title="Located Map"]')
        driver.switch_to.frame(iframe)
        logger.info("Switched to iframe with SUCCESS ")
        time.sleep(30)
        data_iframe = html.fromstring(driver.page_source)
        xpath_stores = '//div[contains(@id, "card") and contains(@class, "card")]'
        data_stores = data_iframe.xpath(xpath_stores)
        logger.info(f"Data object from iframe: {data_stores}")
        for idx, pd in enumerate(data_stores):
            locator_domain = DOMAIN

            # Page URL
            page_url = MISSING
            logger.info(
                f"{idx} out of {len(data_stores)} Stores][Pulling the data from: {page_url} "
            )

            # Location Name
            locname = "".join(pd.xpath(".//div/h5/text()")).strip()

            location_name = locname.split(",")[0].strip()
            location_name = location_name if location_name else MISSING
            logger.info(f"[Location Name: {location_name}]")

            address_from_map = "".join(pd.xpath(".//div[1]/div/text()")).strip()
            logger.info(f"Raw Address: {address_from_map}")

            # Street Address
            ra_scp = address_from_map.split(",")
            street_address = ra_scp[0].strip()
            street_address = street_address if street_address else MISSING
            logger.info(f"[Street Address: {street_address}]")

            # City
            try:
                city = ra_scp[1].strip()
            except Exception:
                city = MISSING
            logger.info(f"[City: {city}]")

            # State
            state = ra_scp[2].strip()
            state = state if city else MISSING
            logger.info(f"[State: {state}]")

            # Zipcode
            zip_postal = ra_scp[3].strip()
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[Zip: {zip_postal}]")

            # Country Code
            country_code = "US"

            # Store Number
            store_number = ""
            store_number = store_number if store_number else MISSING
            logger.info(f"[Store Number: {store_number}]")

            # Phone
            phone = "".join(pd.xpath('.//a[contains(@href, "tel:")]//text()')).strip()
            phone = phone if phone else MISSING

            # Location Type
            location_type = MISSING

            # Latitude
            for ll in latlng:
                if location_name.lower() in ll["location_name"].lower():
                    lat = ll["latitude"]
                    lng = ll["longitude"]

                else:
                    continue
            latitude = lat
            logger.info(f"[Latitude: {latitude}]")

            # Longitude
            longitude = lng
            logger.info(f"[Longitude: {longitude}]")

            # Hours of operation
            hoo = "".join(
                pd.xpath(
                    './/div[div[contains(@class, "far fa-clock col-1 mt-1")]]//div/text()'
                )
            ).strip()
            hours_of_operation = hoo if hoo else MISSING
            logger.info(f"[Hours of Operation: {hours_of_operation}]")

            # Raw Address
            raw_address = address_from_map
            raw_address = raw_address if raw_address else MISSING
            logger.info(f"[Raw Address: {raw_address}]")

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
