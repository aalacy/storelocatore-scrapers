from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "americasmattress_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
}

DOMAIN = "https://www.americasmattress.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.americasmattress.com/gadsden/locations/finderajax"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            latitude = loc["latitude"]
            longitude = loc["longtitude"]
            store_number = loc["id"]
            page_url = DOMAIN + loc["url"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    location_name = soup.find(
                        "h2", {"class": "locations--store-title"}
                    ).text
                except:

                    continue
                street_address = (
                    soup.find("span", {"class": "locations--store-address-line1"}).text
                    + " "
                    + soup.find(
                        "span", {"class": "locations--store-address-line1"}
                    ).text
                )
                if "Coming Soon" in street_address:
                    continue
                address = soup.find(
                    "span", {"class": "locations--store-city"}
                ).text.split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
                country_code = "US"
                try:
                    phone = (
                        soup.find("div", {"class": "locations--store-phone"})
                        .get_text(separator="|", strip=True)
                        .replace("|", "")
                    )
                except:
                    phone = soup.find("span", {"class": "locations--store-phone"}).text
                hours_of_operation = address = (
                    soup.find("div", {"class": "locations--store-time"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
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
