import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "commoncentsstores_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://commoncentsstores.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        page_list = "https://commoncentsstores.com/site/locations"
        r = session.get(page_list, headers=headers)
        soup = BeautifulSoup(r, "html.parser")
        page_list = (
            soup.find("div", {"class": "pagination system_pagination"})
            .findAll("li")[-2]
            .text
        )
        page_list = int(page_list) + 1
        for idx in range(1, page_list):
            log.info(f"Fecthing locations from Page {idx}")
            url = (
                "https://commoncentsstores.com/site/locations?&page="
                + str(idx)
                + "&prop_ModuleId=6268"
            )
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r, "html.parser")
            loclist = soup.findAll("div", string=re.compile("Location Info"))
            for loc in loclist:
                page_url = DOMAIN + loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = soup.find("h1").text
                phone = (
                    soup.select("a[href*=tel]")[-1]
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                )
                address = soup.find("h4").get_text(separator="|", strip=True).split("|")
                if len(address) > 2:
                    address = address[1:]
                street_address = address[0]
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
                country_code = "US"
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
                    latitude=MISSING,
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
