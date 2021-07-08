import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "snipits_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

DOMAIN = "https://www.snipits.com/"
MISSING = "<MISSING>"


def fetch_data():
    final_data = []
    if True:
        url = "https://www.snipits.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "locationResults"}).findAll(
            "div", {"class": "loc-result"}
        )
        for link in linklist:
            temp = link.find("h4").find("a")
            location_name = temp.text
            page_url = temp["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers, verify=False)
            loc = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>", 1
            )[0]
            loc = json.loads(loc)
            phone = loc["telephone"]
            try:
                latitude = loc["geo"]["latitude"]
                longitude = loc["geo"]["longitude"]
            except:
                latitude = MISSING
                longitude = MISSING
            street_address = loc["address"]["streetAddress"]
            city = loc["address"]["addressLocality"]
            state = loc["address"]["addressRegion"]
            zip_postal = loc["address"]["postalCode"]
            country_code = loc["address"]["addressCountry"]
            location_type = loc["@type"]
            hours_of_operation = (
                str(loc["openingHours"])
                .replace("'", "")
                .replace("]", "")
                .replace("[", "")
            )
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
