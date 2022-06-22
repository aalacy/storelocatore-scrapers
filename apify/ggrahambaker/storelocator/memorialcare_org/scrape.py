import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "memorialcare.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.memorialcare.org/"
MISSING = SgRecord.MISSING


def fetch_data():
    api_url = (
        "https://www.memorialcare.org/api/location-search-lookup?&proximity[value]=75"
    )
    locs = session.get(api_url, headers=headers).json()
    for loc in locs:
        store_number = loc["id"]
        page_url = DOMAIN[:-1] + loc["url"]
        log.info(page_url)
        location_type = loc["location_type"].replace("&amp;", "&")
        latitude = loc["lat"]
        longitude = loc["lon"]
        location_name = loc["title"]
        street_address = loc["address_line_1"]
        city = loc["city"]
        state = loc["state"]
        zip_postal = loc["zip"]
        country_code = "US"
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        try:
            phone = (
                soup.find("div", {"class": "location-marquee__contact-info"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
                .replace("Phone:", "")
            )
        except:
            phone = MISSING
        hour_list = soup.find("div", {"class": "open-hours__description"})
        if hour_list:
            hour_list = hour_list.findAll("p")
            hours_of_operation = ""
            for hour in hour_list:
                hour = hour.text
                if "(" in hour:
                    hour = hour.split("(")[0]
                hours_of_operation = hours_of_operation + " " + hour
        else:
            hours_of_operation = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
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
