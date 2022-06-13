from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tacodiner_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://tacodiner.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://tacodiner.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("div", {"class": "fusion-aligncenter"})
        for link in linklist:
            link = link.find("a")["href"]
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("a", {"class": "local-button"})
            for loc in loclist:
                if "Details" not in loc.text:
                    continue
                page_url = loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    location_name = soup.find("h1").text
                except:
                    continue
                temp = (
                    soup.findAll("meta", {"property": "og:description"})[1]["content"]
                    .replace("\r", "")
                    .split("\n")
                )
                location_name = temp[0]
                address = temp[4].strip().split(",")
                street_address = address[0]
                city = address[1]
                address = address[2].split()
                state = address[0]
                zip_postal = address[1]
                phone = temp[6]
                hours_of_operation = temp[-2] + " " + temp[-1]
                hours_of_operation = hours_of_operation.replace(
                    "View Our Menu  We Deliver  Connect", ""
                )
                latitude = r.text.split('"latitude":"')[1].split('"')[0]
                longitude = r.text.split('"longitude":"')[1].split('"')[0]
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
