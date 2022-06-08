from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "littlesprouts_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://littlesprouts.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://littlesprouts.com/schools/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("div", {"class": "x-container max width"})
        for link in linklist:
            loclist = link.findAll("div", {"class": "x-column x-sm x-1-4"})
            for loc in loclist:
                try:
                    page_url = loc.find(
                        "a", {"class": "x-btn purple-btn x-btn-small x-btn-block"}
                    )["href"]
                except:
                    continue
                page_url = "https://littlesprouts.com" + page_url
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                if r.url == "https://littlesprouts.com":
                    hours_of_operation = MISSING
                    phone = MISSING
                    temp = loc.get_text(separator="|", strip=True).split("|")
                    location_name = temp[0]
                    address = temp[1]
                else:
                    soup = BeautifulSoup(r.text, "html.parser")
                    longitude, latitude = (
                        soup.select_one("iframe[src*=maps]")["src"]
                        .split("!2d", 1)[1]
                        .split("!2m", 1)[0]
                        .split("!3d")
                    )
                    if "!3m" in latitude:
                        latitude = latitude.split("!3m")[0]
                    location_name = soup.find("h1").text
                    address = (
                        soup.select_one('p:contains("View Map")')
                        .text.split("|")[0]
                        .strip()
                    )

                    hours_of_operation = (
                        soup.select_one('h4:contains("Hours")')
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .replace("Days:", "")
                    )
                    phone = soup.select_one("a[href*=tel]").text
                address = address.split(",")
                street_address = address[0]
                city = address[1]
                address = address[2].split()
                state = address[0]
                try:
                    zip_postal = address[1]
                except:
                    zip_postal = MISSING
                country_code = "US"
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
