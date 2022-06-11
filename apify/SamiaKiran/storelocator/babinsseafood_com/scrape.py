from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "babinsseafood_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://babinsseafood.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.babinsseafood.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "SubMenu-1"}).findAll("li")
        for loc in loclist:
            page_url = "https://www.babinsseafood.com" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text
            temp = soup.findAll("div", {"class": "col-md-6"})[0]
            address = temp.findAll("a")
            phone = address[1].text
            address = address[0].get_text(separator="|", strip=True).split("|")
            street_address = address[0].replace(",", "")
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            hours_of_operation = (
                temp.findAll("p")[1].get_text(separator="|", strip=True).split("|")[0]
            )
            country_code = "US"
            coords = soup.find("div", {"class": "gmaps"})[
                "data-gmaps-static-url-mobile"
            ]
            coords = coords.split("en¢er=")[1].split("&zoom")[0].split("%2C")
            latitude = coords[0]
            longitude = coords[1]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
