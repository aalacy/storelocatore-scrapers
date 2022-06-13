import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "completecash_net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.completecash.net/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://locations.completecash.net/"
        r = session.get(url, headers=headers)
        loclist = json.loads(
            r.text.split('"features":')[2].split('},"uiLocationsList":')[0]
        )
        for loc in loclist:
            store_number = str(loc["properties"]["id"])
            page_url = "https://locations.completecash.net/" + loc["properties"]["slug"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = json.loads(
                r.text.split('  <script type="application/ld+json">')[2].split(
                    "</script>"
                )[0]
            )
            location_name = temp["name"]
            phone = temp["telephone"]
            street_address = soup.find("span", {"itemprop": "streetAddress"}).text
            city = soup.find("span", {"itemprop": "addressLocality"}).text
            state = soup.find("span", {"itemprop": "addressRegion"}).text
            zip_postal = soup.find("span", {"itemprop": "postalCode"}).text
            country_code = soup.find("span", {"itemprop": "addressCountry"}).text
            latitude = str(temp["geo"]["latitude"])
            longitude = str(temp["geo"]["longitude"])
            hour_list = temp["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + hour["dayOfWeek"]
                    + " "
                    + hour["opens"]
                    + "-"
                    + hour["closes"]
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
