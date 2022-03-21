import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "stonehouserestaurants_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.stonehouserestaurants.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.stonehouserestaurants.co.uk/ourvenues"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.select("a[href*=nationalsearch]")[1:]
        for loc in loclist:
            page_url = loc["href"]
            if DOMAIN not in page_url:
                page_url = DOMAIN + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.find("section", {"class": "premise"})
            location_name = temp.find("p", {"class": "h1"}).text
            temp = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>"
            )[0]
            temp = json.loads(temp)
            location_name = temp["name"]
            phone = temp["telephone"]
            street_address = temp["address"]["streetAddress"]
            city = temp["address"]["addressLocality"]
            try:
                state = temp["address"]["addressRegion"]
            except:
                state = MISSING
            zip_postal = temp["address"]["postalCode"]
            country_code = temp["address"]["addressCountry"]
            latitude = temp["geo"]["latitude"]
            longitude = temp["geo"]["longitude"]

            hours_of_operation = (
                soup.find("ul", {"class": "the-times weekly-schedule"})
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
