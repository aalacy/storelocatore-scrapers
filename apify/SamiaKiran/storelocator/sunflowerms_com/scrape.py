from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "sunflowerms_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.cornermarketms.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "store-listing-rows"}).findAll(
            "div", {"class": "store-list-row-container store-bucket filter-rows"}
        )
        for loc in loclist:
            temp = loc.find("div", {"class": "store-list-row-item-col03"}).findAll("a")
            store_number = temp[0]["data-store_id"]
            location_name = loc.find("a", {"class": "store-name"}).text
            log.info(location_name)
            phone = soup.select_one("a[href*=tel]").text
            address = (
                loc.find("div", {"class": "store-address"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            try:
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
            except:
                state = address[0]
                zip_postal = "<MISSING>"
            hours_of_operation = loc.find(
                "div", {"class": "store-list-row-item-col02"}
            ).text
            latitude, longitude = temp[2]["href"].split("/")[-1].split(",")
            yield SgRecord(
                locator_domain="https://www.cornermarketms.com/",
                page_url="https://www.cornermarketms.com/locations/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type="<MISSING>",
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
