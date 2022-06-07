import json
import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "9round_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.9round.ca"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.9round.ca/locations/directory"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("li", {"class": "pb-1"})
        for loc in loclist:
            url = "https://www.9round.ca" + loc.find("a")["href"]
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            state_list = soup.findAll("a", {"class": "lead"})
            for link in state_list:
                page_url = "https://www.9round.ca" + link["href"]
                r = session.get(page_url, headers=headers)

                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    temp = r.text.split("<script type='application/ld+json'>")[1].split(
                        "</script>", 1
                    )[0]
                except:
                    continue
                if "coming-soon-modal" in r.text:
                    location_type = "Coming Soon"
                else:
                    location_type = "<MISSING>"
                log.info(page_url)
                temp = json.loads(temp)
                location_name = html.unescape(temp["name"])
                latitude = temp["geo"]["latitude"]
                longitude = temp["geo"]["longitude"]
                hours_of_operation = temp["openingHours"]
                try:
                    phone = (
                        soup.select_one("a[href*=tel]")
                        .text.replace("\n", "")
                        .replace("Call: ", "")
                    )
                except:
                    phone = "<MISSING>"
                street_address = html.unescape(temp["address"]["streetAddress"])
                city = html.unescape(temp["address"]["addressLocality"])
                state = temp["address"]["addressRegion"]
                zip_postal = temp["address"]["postalCode"]
                country_code = "CA"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=location_type,
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
