from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "makerpizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.makerpizza.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://api.tattleapp.com/v2/api/locations?expand=address&merchants_id=2308&page=1&size=300"
        loclist = session.get(url, headers=headers).json()["_embedded"]["locations"]
        url = "https://www.makerpizza.com/#find_us"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hour_list = soup.find(
            "div", {"class": "address-group address-group-hours"}
        ).findAll("div", {"class": "address-line"})
        phone = soup.select_one("a[href*=tel]").text.replace("T", "")
        zip_list = soup.findAll("address")
        for loc, hour, temp_zip in zip(loclist, hour_list, zip_list):
            location_name = loc["label"]
            log.info(location_name)
            store_number = loc["id"]
            loc = loc["address"]
            street_address = loc["address_one"]
            city = loc["city"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            state = loc["state"]
            zip_postal = temp_zip.get_text(separator="|", strip=True).split("|")[-2]
            country_code = "CA"
            hours_of_operation = hour.get_text(separator="|", strip=True).split("|")[1:]
            hours_of_operation = " ".join(hours_of_operation)
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
