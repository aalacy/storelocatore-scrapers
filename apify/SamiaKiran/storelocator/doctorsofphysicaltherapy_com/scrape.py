import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "doctorsofphysicaltherapy_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://doctorsofphysicaltherapy.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://doctorsofphysicaltherapy.com/our-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.select("a[href*=stores]")
        for loc in loclist:
            page_url = loc["href"]
            location_type = MISSING
            if "coming-soon" in page_url:
                location_type = "Temporarily Closed"
            if "doctorsofphysicaltherapy" not in page_url:
                page_url = DOMAIN + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            temp = r.text.split('"locations":[')[1].split("]};")[0]
            temp = json.loads(temp)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = temp["store"]
            try:
                street_address = temp["address"] + " " + temp["address2"]
            except:
                street_address = temp["address"]
            city = temp["city"]
            state = temp["state"]
            zip_postal = temp["zip"]
            latitude = temp["lat"]
            longitude = temp["lng"]
            store_number = temp["id"]
            phone = soup.find("div", {"class": "wpsl-contact-details"}).find("a").text
            hours_of_operation = (
                soup.find("table", {"class": "wpsl-opening-hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
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
                store_number=store_number,
                phone=phone,
                location_type=location_type,
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
