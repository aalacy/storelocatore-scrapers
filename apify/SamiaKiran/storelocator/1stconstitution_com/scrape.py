from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "1stconstitution_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://www.1stconstitution.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.1stconstitution.com/wp-admin/admin-ajax.php?action=store_search&lat=40.32772&lng=-74.50554&max_results=50&search_radius=1000&autoload=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["store"]
            store_number = loc["id"]
            log.info(location_name)
            phone = loc["phone"]
            hours_of_operation = loc["hours"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = (
                hours_of_operation.find("table")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            zip_postal = loc["zip"]
            country_code = loc["country"]
            state = loc["state"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            page_url = "https://www.1stconstitution.com/locations/"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
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
