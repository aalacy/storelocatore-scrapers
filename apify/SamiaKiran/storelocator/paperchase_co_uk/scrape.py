import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "paperchase_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.paperchase.com/en_gb/"
MISSING = SgRecord.MISSING


def parse_address(address):
    pa = parse_address_intl(address)

    street_address = pa.street_address_1
    street_address = street_address if street_address else MISSING

    city = pa.city
    city = city.strip() if city else MISSING

    state = pa.state
    state = state.strip() if state else MISSING

    zip_postal = pa.postcode
    zip_postal = zip_postal.strip() if zip_postal else MISSING

    return street_address, city, state, zip_postal


def fetch_data():
    if True:
        url = "https://www.paperchase.com/en_gb/stores.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        untill = (
            soup.find("ul", {"class": "paginator-wrap"})
            .findAll("li")[-2]
            .find("button")
            .text.strip()
        )
        for link in range(1, int(untill) + 1):
            url = "https://www.paperchase.com/en_gb/stores.html?p=" + str(link)
            log.info(f"Fetching links from Page No {link}")
            main_r = session.get(url, headers=headers)
            soup = BeautifulSoup(main_r.text, "html.parser")
            loclist = soup.find("div", {"class": "mb-64 md:mb-0"}).findAll(
                "div", {"class": "mb-16"}
            )
            for loc in loclist:
                page_url = "https://www.paperchase.com" + loc.find("a")["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                loc = (
                    r.text.split('<script type="application/ld+json"')[1]
                    .split('{"@context":"http://schema.org",')[1]
                    .split("</script>")[0]
                )
                loc = json.loads("{" + loc)
                address = loc["address"]
                street_address = address["streetAddress"]
                if "undefined" in street_address:
                    address = loc.get_text(separator="|", strip=True).split("|")
                    location_name = address[0]
                    raw_address = address[1]
                    street_address, city, state, zip_postal = parse_address(raw_address)
                    country_code = address[3]
                    phone = MISSING
                    hours_of_operation = MISSING
                else:
                    try:
                        location_name = loc["name"]
                    except:
                        location_name = MISSING
                    raw_address = (
                        address["streetAddress"]
                        + " "
                        + address["addressLocality"]
                        + " "
                        + address["postalCode"]
                    )
                    street_address, city, state, zip_postal = parse_address(raw_address)
                    country_code = address["addressCountry"]
                    phone = loc["telephone"]
                    hour_list = loc["openingHoursSpecification"]
                    hours_of_operation = ""
                    for hour in hour_list:
                        day = (
                            str(hour["dayOfWeek"])
                            .replace("'", "")
                            .replace("[", "")
                            .replace("]", "")
                        )
                        open_time = hour["opens"]
                        try:
                            closes = hour["closes"]
                        except:
                            closes = ""
                        hours_of_operation = (
                            hours_of_operation
                            + " "
                            + day
                            + " "
                            + open_time
                            + "-"
                            + closes
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
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address.replace("\n", " ").strip(),
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
