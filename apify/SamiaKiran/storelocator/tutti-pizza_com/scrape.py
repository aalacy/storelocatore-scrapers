import re
import json
import html
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tutti-pizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://tutti-pizza.com"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        url = "https://pizzerias.tutti-pizza.com/search?geo=&lat=&lon=&query="
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        page_list = soup.find("ul", {"class": "lf-pagination__list"}).findAll("li")[-2]
        page_list = page_list.get_text(separator="|", strip=True).replace("|", "")
        page_list = int(page_list) + 1
        for page in range(1, page_list):
            log.info(f"Fetching locations from the page {page} ...")
            url_page = (
                "https://pizzerias.tutti-pizza.com/search?geo=&lat=&lon=&page="
                + str(page)
                + "&query="
            )
            r = session.get(url_page, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("script", {"type": "application/ld+json"})[1:]
            for loc in loclist:
                loc = loc.text.replace("\n", "")
                loc = json.loads(loc, strict=False)
                location_name = html.unescape(strip_accents(loc["name"]))
                store_number = MISSING
                phone = MISSING
                page_url = "https://pizzerias.tutti-pizza.com" + loc["url"]
                log.info(page_url)
                address = loc["address"]
                street_address = html.unescape(strip_accents(address["streetAddress"]))
                city = html.unescape(strip_accents(address["addressLocality"]))
                state = MISSING
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
                latitude = loc["geo"]["latitude"]
                longitude = loc["geo"]["longitude"]
                hours_of_operation = loc["openingHours"]
                hours_of_operation = re.sub(pattern, "\n", hours_of_operation)
                hours_of_operation = hours_of_operation.replace("\n", " ")
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
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
