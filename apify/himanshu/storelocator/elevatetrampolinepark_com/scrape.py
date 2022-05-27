import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "elevatetrampolinepark_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
DOMAIN = "https://elevatetrampolinepark.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    r = session.get(DOMAIN)
    soup = BeautifulSoup(r.text, "lxml")
    for location in soup.find_all(
        "a", {"class": re.compile(r"et_pb_button et_pb_button_.+")}
    ):
        page_url = location["href"]
        log.info(page_url)
        location_request = session.get(page_url)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        location_name = location_soup.title.text.replace(
            "is the premier extreme recreation park!", ""
        ).strip()
        if location_soup.find("h4") is None:
            continue
        if location_soup.find("div", {"class": "textwidget"}) is None:
            continue
        address = list(
            location_soup.find("div", {"class": "textwidget"}).stripped_strings
        )
        phone = address[-2]
        if "info" in phone:
            phone = address[-3]
        street_address = address[0]
        address = address[1].split(",")
        city = address[0]
        address = address[1].split()
        state = address[0]
        zip_postal = address[1]
        country_code = "US"
        try:
            geo_location = location_soup.find(
                "iframe", {"data-src": re.compile("/maps/")}
            )["data-src"]
        except:
            geo_location = location_soup.find("iframe", {"src": re.compile("/maps/")})[
                "src"
            ]
        latitude = geo_location.split("!3d")[1].split("!")[0]
        longitude = geo_location.split("!2d")[1].split("!")[0]
        hours_of_operation = (
            location_soup.find_all("div", {"class": "textwidget"})[-1]
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
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
