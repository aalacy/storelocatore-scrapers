import json
import html
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "snipes_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.snipes.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.snipes.com/storefinder"
        r = session.get(url, headers=headers)
        country_list = r.text.split('data-template-attrs="')[1].split(
            '" data-is-dialog-link'
        )[0]
        country_list = country_list.split("url&quot;:&quot;")[1:]
        log.info("Fetching each country's Store Locator...")
        linklist = []
        for country in country_list:
            country = country.split("&quot;")[0]
            country = "https://" + country + "/storefinder"
            if "usa" in country:
                continue
            if country in linklist:
                continue
            linklist.append(country)
        for link in linklist:
            r = session.get(link, headers=headers)
            country_code = country
            log.info(f"Fetching  Stores from {link}")
            try:
                loclist = (
                    r.text.split('data-locations="')[1]
                    .split("data-icon=")[0]
                    .replace('}]"', "}]")
                )
            except:
                continue
            loclist = BeautifulSoup(loclist, "html.parser")
            try:
                loclist = json.loads(str(loclist))
            except:
                continue
            for loc in loclist:
                store_number = loc["id"]
                page_url = "https://www.snipes.com/storedetails?sid=" + store_number
                log.info(page_url)
                location_name = loc["name"] + " Store"
                latitude = loc["latitude"]
                longitude = loc["longitude"]
                loc = loc["infoWindowHtml"]
                loc = (
                    loc.replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .replace("\n", "")
                    .strip()
                )
                soup = BeautifulSoup(loc, "html.parser")
                address = soup.findAll(
                    "div", {"class": "b-store-locator-result-address-section"}
                )
                address = " ".join(x.text for x in address)
                address = strip_accents(address)
                raw_address = html.unescape(address)
                formatted_addr = parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address is None:
                    street_address = formatted_addr.street_address_2
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city if formatted_addr.city else SgRecord.MISSING
                state = (
                    formatted_addr.state if formatted_addr.state else SgRecord.MISSING
                )
                zip_postal = formatted_addr.postcode
                zip_postal = zip_postal.strip() if zip_postal else SgRecord.MISSING
                try:
                    phone = soup.select_one("a[href*=tel]")["href"].replace("tel:", "")
                except:
                    phone = MISSING
                hours_of_operation = (
                    soup.find(
                        "div",
                        {
                            "class": "b-store-locator-store-hours b-store-map-view-section"
                        },
                    )
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
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
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
                    raw_address=raw_address,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
