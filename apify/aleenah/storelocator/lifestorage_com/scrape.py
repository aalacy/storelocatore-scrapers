import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "lifestorage_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://www.lifestorage.com/"
MISSING = "<MISSING>"


def fetch_data():
    res = session.get("https://www.lifestorage.com/")
    soup = BeautifulSoup(res.text, "html.parser")
    sls = soup.find("div", {"class": "footerStates"}).find_all("a")

    for sl in sls:
        url = "https://www.lifestorage.com" + sl.get("href")
        log.info(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        sa = soup.find_all("a", {"class": "btn store"})
        for a in sa:
            page_url = "https://www.lifestorage.com" + a.get("href")
            log.info(page_url)
            try:
                req = session.get(page_url)
            except:
                continue
            soup = BeautifulSoup(req.text, "lxml")
            data = "".join(
                soup.find_all("script", {"type": "application/ld+json"})[-1].contents
            )
            data = (
                data.replace("[,", "[").replace("}{", "},{").split(',"priceRange"')[0]
                + "}]}"
            )
            js = json.loads(data)["@graph"][0]
            location_name = js["alternateName"]
            store_number = js["branchCode"]
            addr = js["address"]
            street_address = addr["streetAddress"]
            state = addr["addressRegion"]
            city = addr["addressLocality"]
            zip_postal = addr["postalCode"]
            country_code = addr["addressCountry"]
            timl = js["openingHoursSpecification"]
            hours_of_operation = ""
            for l in timl:
                hours_of_operation += (
                    l["dayOfWeek"] + ": " + l["opens"] + " - " + l["closes"] + " "
                )
            if "Sunday:" not in hours_of_operation:
                hours_of_operation += "Sunday: Closed"
            phone = js["telephone"]
            latitude = js["geo"]["latitude"]
            longitude = js["geo"]["longitude"]
            location_type = js["@type"]
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
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
