from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "cloverdalepaint_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.cloverdalepaint.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.cloverdalepaint.com/store-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.find("ul", {"class": "nav L4 active"}).findAll("li")
        for state in state_list:
            state_url = "https://www.cloverdalepaint.com" + state.find("a")["href"]
            r = session.get(state_url, headers=headers)
            loclist = r.text.split("<markers>")[1].split("</script>")[0]
            soup = BeautifulSoup(loclist, "html.parser")
            loclist = soup.findAll("marker")
            for loc in loclist:
                location_type = loc["category"]
                street_address = loc["street"]
                city = loc["city"]
                state = loc["statecode"]
                zip_postal = loc["postalcode"]
                raw_address = (
                    street_address + " " + city + " " + state + " " + zip_postal
                )
                country_code = loc["country"]
                latitude = loc["lat"]
                longitude = loc["lng"]
                store_number = loc["storeid"]
                phone = loc["phone"]
                location_name = loc["name"]
                page_url = (
                    state_url
                    + "/location-detail/"
                    + store_number
                    + "/"
                    + loc["storeurlname"]
                )
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                hours_of_operation = (
                    soup.findAll("div", {"class": "loc-cell"})[1]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Hours", "")
                )
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
                    raw_address=raw_address,
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
