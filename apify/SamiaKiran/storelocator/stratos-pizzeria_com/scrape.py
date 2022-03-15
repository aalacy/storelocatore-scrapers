from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "stratos-pizzeria_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://stratos-pizzeria.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://stratos-pizzeria.com/wp-admin/admin-ajax.php?action=store_search&lat=46.81388&lng=-71.20798&max_results=100&search_radius=500&autoload=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            store_number = loc["id"]
            location_name = loc["store"]
            street_address = loc["address"]
            if not loc["address2"]:
                street_address = loc["address"] + " " + loc["address2"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            page_url = loc["url"]
            log.info(location_name)
            phone = loc["phone"]
            hours_of_operation = BeautifulSoup(loc["hours"], "html.parser")
            hours_of_operation = hours_of_operation.get_text(
                separator="|", strip=True
            ).replace("|", " ")
            country_code = "CA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude.strip(),
                longitude=longitude.strip(),
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
