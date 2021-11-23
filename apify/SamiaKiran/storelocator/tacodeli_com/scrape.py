import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tacodeli_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.tacodeli.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.tacodeli.com/locations/"
        r = session.get(url, headers=headers)
        loclist = json.loads(
            r.text.split("var locationsJson=")[1].split("</script>")[0]
        )
        for loc in loclist:
            location_name = loc["title"]
            page_url = loc["link"]
            log.info(page_url)
            store_number = loc["id"]
            phone = loc["phone"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                street_address = (
                    soup.find("span", {"class": "c-address-street-1"}).text
                    + " "
                    + soup.find("span", {"class": "c-address-street-2"}).text
                )
            except:
                street_address = soup.find("span", {"class": "c-address-street-1"}).text

            city = soup.find("span", {"class": "c-address-city"}).text
            state = soup.find("span", {"class": "c-address-state"}).text
            zip_postal = soup.find("span", {"class": "c-address-postal-code"}).text
            hours_of_operation = (
                soup.find("tbody", {"class": "hours-body"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
