import re
import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "farmerboys_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.farmerboys.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        url = "https://www.farmerboys.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "location"})
        for loc in loclist:
            page_url = DOMAIN + loc.find("a")["href"].replace(
                "location-detail.php?loc=", ""
            )
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            schema = r.text.split("<script type='application/ld+json'>")[1].split(
                "</script>", 1
            )[0]
            schema = schema.replace("\n", "")
            schema = re.sub(pattern, "\n", schema)
            loc = json.loads(schema, strict=False)
            location_name = loc["name"]
            address = loc["address"]
            phone = loc["contactPoint"]["telephone"].replace("\n", " ")
            street_address = address["streetAddress"].replace("\n", " ")
            city = address["addressLocality"]
            state = MISSING
            zip_postal = address["postalCode"]
            country_code = address["addressCountry"]
            hours_of_operation = (
                BeautifulSoup(loc["openingHours"], "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace(">/br>", " ")
            )
            try:
                longitude, latitude = (
                    soup.select_one("iframe[src*=maps]")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d")
                )
            except:
                longitude = MISSING
                latitude = MISSING
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
