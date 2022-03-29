import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "moesitaliansandwiches_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.moesitaliansandwiches.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.moesitaliansandwiches.com/locations"
        r = session.get(url, headers=headers)
        loclist = r.text.split('<script type="application/ld+json">')[1:]
        coords_list = r.text.split('"lat":')[1:]
        for loc in loclist:
            loc = json.loads(loc.split("</script>")[0])
            location_name = loc["name"]
            address = loc["address"]
            phone = address["telephone"]
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            zip_postal = address["postalCode"]
            for coords in coords_list:
                if str(phone) in coords:
                    coords = coords.split(',"googlePlaceId"')[0].split(",")
                    latitude = coords[0]
                    longitude = coords[1].replace('"lng":', "")
                    break
            country_code = "US"
            page_url = DOMAIN + city.lower()
            log.info(page_url)
            hours_of_operation = loc["openingHours"]
            hours_of_operation = " ".join(hours_of_operation)
            country_code = "US"
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
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
