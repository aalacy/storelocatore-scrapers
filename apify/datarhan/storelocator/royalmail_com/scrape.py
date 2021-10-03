# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicZipAndGeoSearch, SearchableCountries
from sglogging import sglog


def fetch_data():
    session = SgRequests(proxy_country="gb")

    start_url = "https://www.royalmail.com/capi/rml/bf/v1/locations/branchFinder?postCode={}&latitude={}&longitude={}&searchRadius=40&count=5&selectedName=&officeType=csp&type=undefined&appliedFilters=undefined"
    domain = "royalmail.com"
    log = sglog.SgLogSetup().get_logger(logger_name=domain)
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    codes = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=40
    )
    for zipcode, coord in codes:
        url = start_url.format(zipcode, coord[0], coord[1])
        all_locations = session.get(url, headers=hdr)
        if all_locations.status_code != 200:
            log.info(f"Status Code: {all_locations.status_code}")
            continue
        for poi in all_locations.json():
            raw_address = poi["officeDetails"]["address1"]
            if poi["officeDetails"]["address2"]:
                raw_address += " " + poi["officeDetails"]["address2"]
            if poi["officeDetails"]["address3"]:
                raw_address += " " + poi["officeDetails"]["address3"]
            if poi["officeDetails"]["address4"]:
                raw_address += " " + poi["officeDetails"]["address4"]
            if poi["officeDetails"]["address5"]:
                raw_address += " " + poi["officeDetails"]["address5"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if street_address and addr.street_address_2:
                street_address += " " + addr.street_address_2
            else:
                street_address = addr.street_address_2
            hoo = []
            for e in poi["businessDays"]:
                day = e["businessDay"]
                if e["openingTimes"]:
                    opens = e["openingTimes"][0]["opensAt"]
                    closes = e["openingTimes"][0]["closesAt"]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.royalmail.com/services-near-you#/",
                location_name=poi["officeDetails"]["name"],
                street_address=street_address,
                city=addr.city,
                state=poi["officeDetails"]["county"],
                zip_postal=poi["officeDetails"]["postcode"],
                country_code="",
                store_number="",
                phone="",
                location_type="",
                latitude=poi["locationDetails"]["latitude"],
                longitude=poi["locationDetails"]["longitude"],
                hours_of_operation=hoo,
            )

            yield item


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
