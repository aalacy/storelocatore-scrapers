from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bostonteaparty_co_uk "
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://bostonteaparty.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://bostonteaparty.co.uk/cafes.php?menu=open"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "cafe-col"})
        for loc in loclist:
            if "COMING SOON" in loc.text:
                continue
            location_name = loc.find("h2").text
            page_url = "https://bostonteaparty.co.uk" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            street_address = (
                soup.find("span", {"itemprop": "street-address"})
                .text.replace("\n", " ")
                .replace(",", " ")
            )
            if "Cheswick Village" in street_address:
                street_address = street_address.split("Cheswick Villag")[0]
            city = soup.find("span", {"itemprop": "locality"}).text
            state = MISSING
            zip_postal = soup.find("div", {"itemprop": "postal-code"}).text
            phone = soup.find("span", {"itemprop": "tel"}).text
            hours_of_operation = soup.findAll("div", {"class": "address-info"})[
                1
            ].findAll("p")
            if len(hours_of_operation) > 1:
                hours_of_operation = (
                    hours_of_operation[1]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            else:
                hours_of_operation = (
                    hours_of_operation[0]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            hours_of_operation = (
                hours_of_operation.replace("Daily", "")
                .replace("Regular opening hour", "")
                .replace("Temporary Opening Hours", "")
            )
            country_code = "UK"
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
