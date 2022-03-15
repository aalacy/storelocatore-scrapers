from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "mvsb_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.mvsb.com"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.mvsb.com/about/locations/?doing_wp_cron=1622534811.0141370296478271484375"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = str(soup.find("div", {"class": "accordion-locations"}))
    divlist = divlist.split("<h3")[1:]
    for div in divlist:
        if "Coming" in div:
            continue
        div = "<h3" + div
        div = BeautifulSoup(div, "html.parser")
        branchlist = div.findAll("strong")
        city = div.find("h3").text
        for i in range(0, len(branchlist)):
            title = div.findAll("strong")[i].text
            log.info(title)

            try:
                street = (
                    div.findAll("p")[i].text.split(title, 1)[1].split("(Drive", 1)[0]
                )
            except:
                street = div.text.split(title, 1)[1].split("(Drive", 1)[0]
            phone = (
                div.findAll("li", {"class": "phone"})[i].text.split(":", 1)[1].strip()
            )
            hours = (
                div.findAll("div", {"class": "lobby"})[i]
                .text.replace("Lobby Hours", "")
                .replace("\n", " ")
                .strip()
            )
            try:
                street_address = street.split("(Walk", 1)[0]
            except:
                pass
            if "P.O. Box" in street_address:
                street_address = street_address.split("P.O. Box")[0]
            elif "(" in street_address:
                street_address = street_address.split("(")[0]
            street_address = street_address.replace(",", "")
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=title,
                street_address=street_address,
                city=city.strip(),
                state=MISSING,
                zip_postal=MISSING,
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
