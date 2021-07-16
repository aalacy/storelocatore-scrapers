import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "salonrepublic_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


DOMAIN = "https://salonrepublic.com/"
MISSING = "<MISSING>"


def fetch_data():
    url = "https://salonrepublic.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find("div", {"class": "pt-cv-view pt-cv-grid pt-cv-colsys"}).findAll(
        "div", {"class": "pt-cv-ifield"}
    )
    for loc in loclist:
        page_url = loc.find("a")["href"]
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            temp = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>"
            )[0]
        except:
            continue
        temp = json.loads(temp)
        location_name = temp["name"]
        address = temp["address"]
        street_address = address["streetAddress"]
        city = address["addressLocality"]
        state = address["addressRegion"]
        zip_postal = address["postalCode"]
        country_code = "US"
        try:
            hours_of_operation = (
                str(temp["openingHours"]).replace('["', "").replace(']"', "")
            )
            phone = temp["telephone"]
        except:
            phone = soup.select_one("a[href*=tel]").text
            hours_of_operation = MISSING
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
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hours_of_operation,
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
