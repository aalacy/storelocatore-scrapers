import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "weldricks_co_uk "
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.weldricks.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.weldricks.co.uk/branches"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "sitemap"}).findAll("li")
        for loc in loclist:
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            temp = r.text.split('<script type="application/ld+json">')[2].split(
                "</script>"
            )[0]
            temp = json.loads(temp)
            location_name = temp["name"]
            address = temp["address"]
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            zip_postal = address["postalCode"]
            country_code = address["addressCountry"]
            latitude = temp["geo"]["latitude"]
            longitude = temp["geo"]["longitude"]
            phone = temp["telephone"]
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text
            temp = soup.findAll("div", {"class": "large-third"})
            location_type = MISSING
            hours_of_operation = (
                temp[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Opening Times", "")
                .replace("Bank Holidays CLOSED", "")
                .replace("|", "")
                .replace("|", "")
            )
            if "branch is now closed" in hours_of_operation:
                continue
            elif "branch is closed" in hours_of_operation:
                continue
            elif "NA" in hours_of_operation:
                hours_of_operation = MISSING
            elif "temporarily closed" in hours_of_operation:
                location_type = "Temporarily Closed"
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
                location_type=location_type,
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
