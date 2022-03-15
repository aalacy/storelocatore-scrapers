import json
import unicodedata
from lxml import etree
from sglogging import sglog
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "jimmychoo_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://row.jimmychoo.com",
    "referer": "https://row.jimmychoo.com/en/store-locator",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


DOMAIN = "https://jimmychoo.com"
MISSING = SgRecord.MISSING


def fetch_data():
    all_locations = []
    start_url = "https://row.jimmychoo.com/en/store-locator"
    r = session.get(start_url)
    soup = BeautifulSoup(r.text, "html.parser")
    countries = soup.findAll("option", {"class": "f-select_option"})
    for country in countries:
        country_code = country.text
        log.info(f"Fetching locations from {country_code}")
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        post_url = dom.xpath('//form[@id="dwfrm_storelocator"]/@action')[0]
        post_url += "&dwfrm_storelocator_findbycountry=ok"
        formdata = {
            "address": country_code,
            "format": "ajax",
            "country": country["value"],
        }
        response = session.post(post_url, data=formdata, headers=headers)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//a[contains(@href, "store-details")]/@href')
        for url in list(set(all_locations)):
            page_url = urljoin(start_url, url)
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            poi = soup.find("div", {"id": "store-details-content"})["data-marker-info"]
            poi = json.loads(poi)
            location_name = soup.find("h1").text
            raw_address = (
                soup.find("div", {"class": "js-store-address"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            raw_address = strip_accents(raw_address)
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            store_number = poi["id"]
            try:
                phone = soup.select_one("a[href*=tel]").text
            except:
                phone = MISSING
            try:
                location_type = (
                    soup.find("div", {"class": "store-types"}).find("p").text
                )
            except:
                location_type = MISSING
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            try:
                hours_of_operation = (
                    soup.find("div", {"class": "store-hours"})
                    .find("p")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                hours_of_operation = MISSING
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
