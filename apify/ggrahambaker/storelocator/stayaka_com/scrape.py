import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "stayaka_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.stayaka.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.stayaka.com/locations"
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        state_list = soup.findAll("ul", {"class": "submenu level-3"})
        for state_url in state_list:
            loclist = state_url.findAll("a")
            for loc in loclist:
                page_url = DOMAIN + loc["href"]
                log.info(page_url)
                response = session.get(page_url, headers=headers)
                if (
                    "We look forward to welcoming guests in late Summer, 2022"
                    in response.text
                ):
                    continue
                elif "welcoming you in September, 2022" in response.text:
                    continue
                soup = BeautifulSoup(response.content, "html.parser")
                cont = json.loads(
                    soup.find("script", {"type": "application/ld+json"}).text
                )
                location_name = cont["name"]
                page_url = cont["url"]
                try:
                    phone = cont["telephone"]
                except:
                    phone = MISSING
                addy = cont["address"]
                try:
                    street_address = (
                        addy["streetAddress"].replace("Cira Centre South,", "").strip()
                    )
                except:
                    street_address = (
                        soup.find("div", {"class": "property-address"})
                        .get_text(separator="|", strip=True)
                        .split("|")[1]
                    )
                city = addy["addressLocality"]
                state = addy["addressRegion"]
                zip_postal = addy["postalCode"]
                country_code = addy["addressCountry"]
                if state == "London":
                    country_code = "GB"
                latitude = cont["geo"]["latitude"]
                longitude = cont["geo"]["longitude"]
                if len(str(latitude)) < 2:
                    latitude = MISSING
                    longitude = MISSING
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
                    hours_of_operation=MISSING,
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
