from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "costlessfoods_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://costlessfoods.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://costlessfoods.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "block_content_photo"})
        for loc in loclist:
            location_name = loc.find("div", {"class": "content_inner"}).find("h2").text
            temp = loc.find("div", {"class": "content_inner"}).findAll("p")
            phone = temp[0].findAll("strong")[1].text
            page_url = temp[3].find("a")["href"]
            page_url = "https://costlessfoods.com" + page_url
            log.info(page_url)
            address = temp[1].findAll("strong")
            street_address = address[0].text
            address = address[1].text.split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            hours_of_operation = temp[2].find("strong").text
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            coords = soup.find("iframe")["src"]
            r = session.get(coords, headers=headers)
            coords = r.text.split("],0],")[0].rsplit("[null,null,", 1)[1].split(",")
            latitude = coords[0]
            longitude = coords[1]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=latitude.strip(),
                longitude=longitude.strip(),
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
