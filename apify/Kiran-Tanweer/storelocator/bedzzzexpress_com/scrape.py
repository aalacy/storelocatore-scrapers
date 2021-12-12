import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "mrgas_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.mrgas.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://bedzzzexpress.com/stores/"
        r = session.get(url, headers=headers)
        coord_list = r.text.split('"markers":')[1].split(", ]}")[0] + "]"
        coord_list = json.loads(coord_list)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "fgm-section pdiv"})
        for loc in loclist:
            temp = loc.find("h2").find("a")
            page_url = "https://bedzzzexpress.com" + temp["href"]
            log.info(page_url)
            location_name = temp.text
            loc = loc.findAll("p")
            address = loc[0].get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            phone = loc[1].text
            hours_of_operation = (
                loc[2].get_text(separator="|", strip=True).replace("|", " ")
            )
            for coord in coord_list:
                if phone in coord["html"]:
                    latitude = coord["latitude"]
                    longitude = coord["longitude"]
                    break
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
