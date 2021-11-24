from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "kingcashsaver_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://api.freshop.com/1/stores?app_key=king_cash_saver&has_address=true&limit=-1"
        loclist = session.get(url, headers=headers).json()["items"]
        for loc in loclist:
            location_name = loc["name"]
            store_number = loc["id"]
            page_url = loc["url"]
            log.info(page_url)
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            phone = loc["phone_md"].split("Fax")[0]
            hours_of_operation = loc["hours_md"]
            street_address = loc["address_1"]
            city = loc["city"]
            zip_postal = loc["postal_code"]
            state = loc["state"]
            yield SgRecord(
                locator_domain="https://www.kingcashsaver.com/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number=store_number,
                phone=phone.strip(),
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
