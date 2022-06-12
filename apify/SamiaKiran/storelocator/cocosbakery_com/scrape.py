import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "cocosbakery_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}

session = SgRequests()
DOMAIN = "https://cocosbakery.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://cocosbakery.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "fusion-column-content-centered"})
        coord_list = r.text.split("addresses: ")[1].split("}],")[0]

        coord_list = json.loads(coord_list + "}]")
        for loc in loclist:
            try:
                location_name = loc.find("h3").text
            except:
                continue
            log.info(location_name)
            temp_list = loc.findAll("p")
            if not temp_list[0].text.strip():
                del temp_list[0]
            raw_address = (
                temp_list[0].get_text(separator="|", strip=True).replace("|", " ")
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
            phone = temp_list[1].find("a").text
            hours_of_operation = (
                temp_list[2]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Now open for dine-in and takeout!", "")
                .replace("Reopening 5/13/2021!", "")
                .replace("Hours:", "")
                .replace("Open for Dine-In", "")
                .replace("Open for Dining", "")
                .replace("Open for Outdoor Dining", "")
                .replace("Open for Dine-in and Takeout", "")
                .replace("Takeout & Delivery", "")
                .replace("Outdoor Dining", "")
                .replace("Open for Indoor Dining", "")
                .replace("Open for Dine-in", "")
                .replace("Takeout", "")
                .replace("Open", "")
                .replace("&", "")
                .replace("for", "")
                .replace(",", "")
                .replace("Dine-in", "")
            )
            location_type = MISSING
            if "Temporarily Closed" in hours_of_operation:
                hours_of_operation = MISSING
                location_type = "Temporarily Closed"
            country_code = "US"
            for coord in coord_list:
                if street_address.split()[0] == coord["address"].strip().split()[0]:
                    latitude = coord["latitude"]
                    longitude = coord["longitude"]
                    break
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
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
