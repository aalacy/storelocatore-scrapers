from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from lxml import html

# Location URL
url_locations = "https://beachhutdeli.com/locations/"


logger = SgLogSetup().get_logger("beachhutdeli_com")

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}

DOMAIN = "https://www.beachhutdeli.com"
base_url = "https://beachhutdeli.com/locations/"
MISSING = "<MISSING>"

session = SgRequests()


def fetch_data():
    url_locations = "https://beachhutdeli.com/locations/"
    r = session.get(url_locations, headers=headers)
    data_r = html.fromstring(r.text, "lxml")
    data_state_list = data_r.xpath("//select[@id='select-state']/option/@value")
    for state in data_state_list[1:]:
        url_state = url_locations + "results/?state=" + state
        logger.info(f"Pulling the data from: {url_state}")
        data_json = session.get(url_state, headers=headers).json()
        for data in data_json:
            logger.info(f"JSON Data:\n {data} \n")
            locator_domain = DOMAIN

            # Page URL
            page_url = data["href"].strip() if data["href"].strip() else MISSING

            # Location Name
            location_name = data["post_title"].strip()
            logger.info(f"location name: {location_name}")

            # Street Address
            address = data["location"]
            sa1 = address["address"].strip()
            sa2 = address["address_2"].strip()
            street_address = ""
            if sa2:
                if sa1:
                    street_address = f"{sa1}, {sa2}"
                else:
                    street_address = sa1
            else:
                street_address = sa1

            street_address = street_address if street_address else MISSING

            city = address["city"].strip() if address["city"] else MISSING
            state = address["state"].strip() if address["state"] else MISSING
            zipcode = address["zip"].strip() if address["zip"] else MISSING

            # Country Code
            country_code = "US"

            # Store Number
            store_number = data["info"]["store_number"].strip()
            store_number = store_number if store_number else MISSING

            # Phone
            phone = data["info"]["phone"].strip()
            phone = phone if phone else MISSING

            # Location Type
            location_type = data["post_type"].strip()
            location_type = location_type if location_type else MISSING

            # Latitude
            latitude = address["latitude"].strip()
            latitude = latitude if latitude else MISSING

            # Longitude
            longitude = address["longitude"].strip()
            longitude = longitude if longitude else MISSING

            # Hourse of Operation
            hours_of_operation = ""
            hoo = " ".join(data["info"]["hours"].strip().split())
            hoo = hoo.replace("<br />", "").strip()
            hours_of_operation = hoo if hoo else MISSING
            if sa2:
                raw_address = f"{sa1}, {sa2}"
            else:
                raw_address = sa1

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
