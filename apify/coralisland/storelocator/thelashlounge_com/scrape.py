import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "thelashlounge_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
}

DOMAIN = "https://www.thelashlounge.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.thelashlounge.com/salons/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "location-bottom-link"})
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            temp = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>"
            )[0]
            temp = json.loads(temp)
            location_name = temp["name"]
            phone = temp["telephone"]
            address = temp["address"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            zip_postal = address["postalCode"]
            street_address = (
                address["streetAddress"]
                .replace("<br/>", "")
                .replace(city, "")
                .replace(state, "")
                .replace(zip_postal, "")
            )
            country_code = address["addressCountry"]
            latitude = str(temp["geo"]["latitude"])
            longitude = str(temp["geo"]["longitude"])
            hours_of_operation = (
                str(temp["openingHours"])
                .replace("'", "")
                .replace("[", "")
                .replace("]", "")
            )
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
