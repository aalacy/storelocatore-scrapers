import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "midwest-dental_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://midwest-dental.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://midwest-dental.com/find-by-zip/"
    r = session.get(url, headers=headers)
    r = r.text.split(" var locs = ")[1].split("}];")[0] + "}]"
    loclist = json.loads(r)
    for loc in loclist:
        location_name = loc["name"]
        latitude = loc["lat"]
        longitude = loc["lng"]
        street_address = loc["address"]
        city = loc["city"]
        state = loc["state"]
        zip_postal = loc["zip"]
        phone = loc["phone"]
        page_url = loc["url"]
        try:
            if page_url.find("https://midwest-dental.com/locations") == -1:
                continue
        except:
            continue
        country_code = "US"
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        if r.status_code != 200:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            hours_of_operation = soup.find("div", {"id": "hours"}).findAll("div")[2:]
            hours_of_operation = " ".join(
                x.get_text(separator="|", strip=True).replace("|", " ")
                for x in hours_of_operation
            )
        except:
            hours_of_operation = MISSING
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
