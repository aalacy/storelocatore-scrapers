from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "ybs_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.ybs.co.uk/index.html"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.ybs.co.uk/assets/ybs-location-data.json"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["Name"]
            page_url = (
                "https://www.ybs.co.uk/contact-us/branch-finder/details.html?location="
                + loc["URL"]
            )
            log.info(location_name)
            location_type = loc["Type"]
            phone = loc["Telephone1"]
            raw_address = (
                loc["Address1"] + " " + loc["Address2"] + " " + loc["Address3"]
            )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING
            if city == MISSING:
                city = location_name
            zip_postal = loc["Postcode"]
            raw_address = raw_address + " " + zip_postal
            country_code = "GB"
            latitude = loc["Lat"]
            longitude = loc["Lng"]
            mo = loc["TimesMonday"]
            tu = loc["TimesTuesday"]
            we = loc["TimesWednesday"]
            th = loc["TimesThursday"]
            fr = loc["TimesFriday"]
            sa = loc["TimesSaturday"]
            su = loc["TimesSunday"]
            hours_of_operation = (
                "Mon "
                + mo
                + " Tue "
                + tu
                + " Wed "
                + we
                + " Thu "
                + th
                + " Fri "
                + fr
                + " Sat "
                + sa
                + " Sun "
                + su
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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
