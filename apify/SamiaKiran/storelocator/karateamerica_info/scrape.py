import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "karateamerica_info"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.karateamerica.info/"
MISSING = SgRecord.MISSING

api_url = "https://mystudio.academy/Api/general/getcompanyDetailsForLandingPage"


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"id": "menu-locations"}).findAll("li")
        log.info("Fetching the Tokens & Id's....")
        for loc in loclist:
            page_url = loc.find("a")["href"]
            if "world-headquarters" in page_url:
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            template_id = (
                soup.findAll("script")[-2]["src"].split("json")[1].split(".")[0]
            )
            store_number = str(r.url).split(".")[0].split("//")[1]
            api_url = (
                "https://"
                + store_number
                + ".prod.live.site.mystudio.io/uploads/customwebsite/"
                + store_number
                + "/live/template_json"
                + template_id
                + ".js"
            )
            r = session.get(api_url)
            loc = r.text.split('"business_name"')[1].split(',"twitter_id"')[0]
            loc = json.loads('{"business_name"' + loc + "}")
            location_name = loc["business_name"]
            phone = loc["business_phone"]
            street_address = loc["business_address1"]
            city = loc["business_address3"]
            state = loc["business_address4"]
            zip_postal = loc["business_address5"]
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
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
