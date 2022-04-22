from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "staples_com__sbd__cre__noheader__staples___studio__index_html"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.staples.com/sbd/cre/noheader/staples_studio/index.html"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "studio_block"})
        api_url = "https://www.staples.com/sbd/cre/noheader/staples_studio/json/locations.json"
        r = session.get(api_url, headers=headers)
        temp_list = r.text.split('"location_name":')[1:]
        for loc in loclist:
            page_url = loc.find("a")["href"]
            if "studio.staples.ca" not in page_url:
                page_url = "https://www.staples.com" + loc.find("a")["href"]
            log.info(page_url)
            location_name = loc.find("div", {"class": "studio_titile white_color"}).text
            address = loc.find("p").get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            if "Canada" in address[-1]:
                address = address[1].split(",")
                city = address[0]
                state = MISSING
                zip_postal = address[1]
                if "Ontario" in zip_postal:
                    state = zip_postal
                    zip_postal = MISSING
                if zip_postal.split()[0] == "BC":
                    state = zip_postal.split()[0]
                    zip_postal = zip_postal.replace("BC", "")
                country_code = "CA"
            else:
                street_address = address[0]
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
                country_code = "US"
            for temp in temp_list:
                if city in temp.split('"address": "')[1].split('",')[0]:
                    phone = temp.split('"phone": "')[1].split('",')[0]
                    hours_of_operation = temp.split('"hours": "')[1].split('",')[0]
                    break
                else:
                    phone = MISSING
                    hours_of_operation = MISSING
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
