from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "henrys_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}


def fetch_data():
    if True:
        url = "https://www.henrys.com/api/stores/getStoreList"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            store_number = loc["StoreId"]
            location_name = loc["StoreName"]
            street_address = loc["Address"].replace("\n", " ")
            city = loc["City"]
            state = loc["Province"]
            zip_postal = loc["PostalCode"]
            phone = loc["LocalPhone"]
            latitude = loc["Latitude"]
            longitude = loc["Longitude"]
            hours = loc["StoreHours"]
            hours = BeautifulSoup(hours, "html.parser")
            day_list = hours.findAll("dt")
            time_list = hours.findAll("dd")
            hours_of_operation = ""
            for d, t in zip(day_list, time_list):
                day = d.text
                time = t.text
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + time + " ".strip()
                )
            page_url = loc["Url"]
            page_url = "https://www.henrys.com/" + page_url
            log.info(page_url)
            yield SgRecord(
                locator_domain="https://www.henrys.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="CA",
                store_number=store_number,
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude.strip(),
                longitude=longitude.strip(),
                hours_of_operation=hours_of_operation,
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
