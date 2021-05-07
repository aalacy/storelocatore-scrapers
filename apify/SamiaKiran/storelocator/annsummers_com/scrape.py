from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "annsummers_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.annsummers.com/on/demandware.store/Sites-AS-GB-Site/en_GB/Stores-FindStores?radius=1000"
        loclist = session.get(url, headers=headers).json()["stores"]
        for loc in loclist:
            location_name = loc["name"]
            page_url = "https://www.annsummers.com" + loc["actionUrl"]
            store_number = loc["ID"]
            log.info(page_url)
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            phone = loc["phone"]
            hours_of_operation = BeautifulSoup(loc["storeHours"], "html.parser")
            hours_of_operation = hours_of_operation.findAll("span")
            hours_of_operation = " ".join(x.text for x in hours_of_operation).split(
                "Bank Holiday:", 1
            )[0]
            if not loc["address2"]:
                street_address = loc["address1"]
            else:
                street_address = loc["address1"] + " " + loc["address2"]
            city = loc["city"]
            zip_postal = loc["postalCode"]
            state = loc["stateCode"]
            country_code = loc["countryCode"]
            yield SgRecord(
                locator_domain="https://www.annsummers.com/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
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
