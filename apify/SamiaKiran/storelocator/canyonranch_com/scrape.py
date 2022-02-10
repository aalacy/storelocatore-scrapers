from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "canyonranch_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.canyonranch.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.canyonranch.com/contact-us/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = (
            soup.find("div", {"id": "main"})
            .findAll("div", {"class": "contacts"})[-1]
            .findAll("div", {"class": "contacts_item"})
        )
        linklist = (
            soup.find("footer").findAll("ul", {"class": "list_reset"})[3].findAll("li")
        )
        hours_of_operation = soup.find(
            "div", {"class": "base_markdown contacts_body"}
        ).findAll("h3")
        hours_of_operation = (
            hours_of_operation[0].text + " " + hours_of_operation[1].text
        )

        for loc, link in zip(loclist, linklist):
            page_url = "https://www.canyonranch.com" + link.find("a")["href"]
            log.info(page_url)
            location_name = loc.find("h3").text
            temp = loc.findAll("a")
            address = temp[0].get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            phone = temp[1].text.replace("(opens in new window)", "")
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
                longitude=MISSING,
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
