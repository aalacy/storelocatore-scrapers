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
website = "sharkeyscutsforkids_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://sharkeyscutsforkids.com"
MISSING = SgRecord.MISSING


def fetch_data():
    start_url = "https://sharkeyscutsforkids.com/locations/"
    r = session.get(start_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "geodir-content"})
    for loc in loclist:
        page_url = loc.find("a")["href"]
        log.info(page_url)
        r = session.get(page_url)
        soup = BeautifulSoup(r.text, "html.parser")
        if '<script type="application/ld+json">' in r.text:
            schema = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>", 1
            )[0]
            schema = schema.replace("\n", "")
            poi = json.loads(schema)
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_postal = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            phone = poi["telephone"]
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            raw_address = street_address + " " + city + " " + state + " " + zip_postal
        else:
            location_name = loc.find("h2").text
            phone = loc.select_one("a[href*=tel]").text
            raw_address = (
                soup.findAll("h2")[1].text.replace(",", "").replace("ðŸ“", "")
            )

            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "US"
            latitude = MISSING
            longitude = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=MISSING,
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
