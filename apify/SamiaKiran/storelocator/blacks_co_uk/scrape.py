import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "blacks_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://blacks.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.blacks.co.uk/stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.select("a[href*=stores]")
        loclist = loclist
        for loc in loclist:
            location_name = loc.text
            page_url = "https://www.blacks.co.uk" + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            try:
                loc = r.text.split('</script><script type="application/ld+json">')[
                    1
                ].split("</script>")[0]
            except:
                continue
            loc = json.loads(loc)
            address = loc["address"]
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            state = MISSING
            zip_postal = address["postalCode"]
            country_code = address["addressCountry"]
            coords = loc["hasmap"].split("@")[1].split(",")
            latitude = coords[0]
            longitude = coords[1]
            phone = loc["telephone"]
            hours_of_operation = str(loc["openingHours"])
            hours_of_operation = (
                hours_of_operation.replace("]", "")
                .replace("[", "")
                .replace(",", " ")
                .replace("'", "")
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
