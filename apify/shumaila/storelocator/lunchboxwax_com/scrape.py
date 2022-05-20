from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "lunchboxwax_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://lunchboxwax.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.lunchboxwax.com/salons/"
    request = session.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    data_list = soup.findAll("li", {"class", "locationcols"})
    for data in data_list:
        temp = data.findAll("span")
        latitude = data["data-lat"]
        longitude = data["data-lon"]
        location_name = temp[0].text
        street_address = temp[1].text
        if "Coming Soon" in street_address:
            continue
        city = temp[2].text
        state = temp[3].text
        zip_postal = temp[4].text
        phone = temp[-1].text
        page_url = data.findAll("a")[-1]["href"]
        log.info(page_url)
        subrequest = session.get(page_url)
        subsoup = BeautifulSoup(subrequest.text, "html.parser")
        try:
            hours_of_operation = (
                subsoup.find("div", {"class", "hidden-hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        except:
            hours_of_operation = MISSING
        country_code = "US"
        if "-" in latitude:
            temp = latitude
            latitude = longitude
            longitude = temp
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
            hours_of_operation=hours_of_operation,
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
