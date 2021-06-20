import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "leevalley_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.leevalley.com/en-us"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.leevalley.com/en-us/storelocations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("li", {"class": "lv-store-location-card"})
        for link in linklist:
            page_url = "https://www.leevalley.com" + link.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            temp = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>"
            )[0]
            temp = json.loads(temp)
            location_name = temp["name"]
            phone = temp["telephone"]
            address = temp["address"]
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            zip_postal = address["postalCode"]
            country_code = "CA"
            state = address["addressRegion"]
            hour_list = temp["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hour_list:
                day = hour["dayOfWeek"]["name"]
                time = hour["opens"] + ": " + hour["closes"]
                hours_of_operation = hours_of_operation + " " + day + " " + time

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
