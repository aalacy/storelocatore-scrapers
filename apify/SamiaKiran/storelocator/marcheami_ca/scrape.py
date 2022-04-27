import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "marcheami_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://marcheami.ca/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://marcheami.ca/map-stores"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = strip_accents(loc[0])
            log.info(location_name)
            phone = loc[3]
            raw_address = strip_accents(loc[2].replace("//", ""))
            latitude, longitude = loc[4].split(",")
            hours_of_operation = (
                loc[5]
                .replace('{ "1" : "', "Mon ")
                .replace('","2" : "', " Tue ")
                .replace('","3" : "', " Wed ")
                .replace('","4" : "', " Thu ")
                .replace('","5" : "', " Fri ")
                .replace('","6" : "', " Sat ")
                .replace('","0" : "', " Sun ")
                .replace('" }', "")
            )
            if "Mon  Tue  Wed  Thu  Fri  Sat  Sun" in hours_of_operation:
                hours_of_operation = MISSING
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            if len(zip_postal) < 5:
                zip_postal = street_address.split()[-1] + " " + zip_postal
                street_address = street_address.replace(street_address.split()[-1], "")
            if "null" in latitude:
                latitude = MISSING
                longitude = MISSING
            country_code = "CA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://marcheami.ca/trouver-magasin",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
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
