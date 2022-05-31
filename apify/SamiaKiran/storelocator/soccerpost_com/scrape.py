from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "soccerpost_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

DOMAIN = "https://soccerpost.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://soccerpost.com/a/store-locator/list"
        r = session.get(url, headers=headers)
        v = r.text.split("geojson.js?v=")[1].split('"')[0]
        url = (
            "https://cdn.shopify.com/s/files/1/0570/1609/0802/t/19/assets/storeifyapps-geojson.js?v="
            + v
        )
        r = session.get(url, headers=headers)
        loclist = r.text.split('type:"Feature"')[1:]
        for loc in loclist:
            location_name = loc.split('name:"')[1].split('"')[0]
            if "COMING SOON!" in location_name:
                continue
            log.info(location_name)
            try:
                phone = loc.split('phone:"')[1].split('"')[0]
            except:
                phone = MISSING
            if "Coming Soon!" in phone:
                phone = MISSING
            longitude, latitude = (
                loc.split("coordinates:[")[1].split("]}")[0].split(",")
            )
            store_number = loc.split("id:")[1].split(",")[0]
            raw_address = loc.split('address:"')[1].split('"')[0]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            if city == MISSING:
                city = raw_address.split(",")[1]
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://soccerpost.com/a/store-locator/list",
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
                hours_of_operation=MISSING,
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
