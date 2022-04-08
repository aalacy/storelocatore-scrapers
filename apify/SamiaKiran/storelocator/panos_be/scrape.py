from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "panos_be"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.panos.be",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.panos.be/nl/onze-winkels?center=50.85034%2C4.35171&zoom=3&latitude=50.85034&longitude=4.35171",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "PreferredCulture=nl-BE; PreferredUICulture=nl-BE",
}


DOMAIN = "https://www.panos.be"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.panos.be/api/Store/Search/7811?within=66.86280419815486%2C-58.75375844999998%2C26.59244565194541%2C67.45717905000004"
        loclist = session.get(url, headers=headers).json()["payload"]["items"]
        for loc in loclist:
            location_name = loc["fullname"]
            try:
                phone = loc["phone"]
            except:
                phone = MISSING
            log.info(location_name)
            raw_address = loc["address"]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "BE"
            latitude = loc["lat"]
            longitude = loc["lng"]
            hour_list = loc["openingHours"]
            hours_of_operation = ""
            for hour in hour_list:
                day = hour["day"]
                time = hour["time"]
                hours_of_operation = hours_of_operation + " " + day + " " + time

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.panos.be/nl/onze-winkels",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
