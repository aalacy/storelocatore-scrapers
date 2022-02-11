import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "loknstore_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.loknstore.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.loknstore.co.uk/self-storage/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find(
            "select", {"class": "form--select__component js-select-store"}
        ).findAll("option")
        for loc in loclist[1:]:
            page_url = loc["value"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                temp = json.loads(
                    r.text.split('<script type="application/ld+json">')[1].split(
                        "</script>"
                    )[0]
                )
                location_name = temp["name"]
                phone = temp["telephone"]
                address = temp["address"]
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
                latitude = str(temp["geo"]["latitude"])
                longitude = str(temp["geo"]["longitude"])

            except:
                location_name = (
                    "Lok'nStore " + soup.find("span", {"class": "store__name"}).text
                )
                phone = soup.find("p", {"class": "store__number"}).text
                address = soup.find(
                    "p", {"class": "store__address__container"}
                ).text.split(",")
                street_address = address[0]
                city = address[1]
                state = address[2]
                zip_postal = address[3]
                country_code = "GB"
                latitude = MISSING
                longitude = MISSING

            hours_of_operation = (
                soup.find("div", {"class": "opening__hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("(Call for information)", "")
                .replace("TBC", "")
            )
            if "CURRENTLY CLOSED" in hours_of_operation:
                location_type = "Temporarily Closed"
            else:
                location_type = MISSING
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
