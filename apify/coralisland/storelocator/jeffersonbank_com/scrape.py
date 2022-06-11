from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "jeffersonbank_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://jeffersonbank.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.jeffersonbank.com/locations/json"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["title"]
            store_number = loc["nid"]
            address = loc["address"]
            address = BeautifulSoup(address, "html.parser")
            address = address.get_text(separator="|", strip=True).split("|")
            if len(address) > 3:
                street_address = address[0] + " " + address[1]
                country_code = address[-1]
                address = address[2].split()
                city = MISSING
                state = address[1]
                zip_postal = address[0]
            else:
                street_address = address[0]
                country_code = address[-1]
                address = address[1].split()
                city = MISSING
                state = address[1]
                zip_postal = address[0]
            log.info(location_name)
            phone = loc["phone"]
            phone = BeautifulSoup(phone, "html.parser")
            phone = phone.text
            hours_of_operation = loc["lobby_hours"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = hours_of_operation.get_text(
                separator="|", strip=True
            ).replace("|", " ")
            coords = loc["field_coordinates"]
            coords = BeautifulSoup(coords, "html.parser")
            coords = (
                coords.text.split(
                    '"coordinates":[',
                )[1]
                .split("]")[0]
                .split(",")
            )
            latitude = coords[1]
            longitude = coords[0]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.jeffersonbank.com/locations/",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
