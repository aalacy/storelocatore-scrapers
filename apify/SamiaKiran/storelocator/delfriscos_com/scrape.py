import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "delfriscos_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.delfriscos.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://delfriscos.com/locations-search/"
        r = session.get(url, headers=headers)
        loclist = r.text.split(" locations: ")[1].split("}}],", 1)[0]
        loclist = loclist + "}}]"
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = loc["name"]
            store_number = loc["id"]
            page_url = "https://www.delfriscos.com/location/" + loc["slug"]
            log.info(page_url)
            latitude = loc["lat"]
            longitude = loc["lng"]
            phone = loc["phone_number"]
            street_address = loc["street"]
            city = loc["city"]
            zip_postal = loc["postal_code"]
            state = loc["state"]
            country_code = "US"
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            hours_of_operation = str(
                soup.find("div", {"class": "row"}).findAll("p")[1]
            ).split("<h4>")[0]
            hours_of_operation = (
                hours_of_operation.replace("<br/>", " ")
                .replace("<br>", " ")
                .replace("<p>", " ")
            )
            if "Open for" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Open for")[0]
            if "Happy Hour" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Happy Hour")[0]
            if "Dine In" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Dine In")[0]
            hours_of_operation = hours_of_operation.replace("</p>", "")
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
                location_type=MISSING,
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
