# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipAndGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://pmi-parking.com/r/parking/garagepoints.aspx?lat={}&lng={}&searchSource=daily&searchAddress={}"
    domain = "pmi-parking.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    codes = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=1
    )
    for zip_code, coords in codes:
        data = session.get(
            start_url.format(coords[0], coords[1], zip_code), headers=hdr
        ).json()
        for i, poi in data.items():
            store_number = poi["GarageId"]
            page_url = (
                f"https://pmi-parking.com/r/parking/view.aspx?record_id={store_number}"
            )
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            state = loc_dom.xpath('//input[contains(@name, "State")]/@value')[0]
            zip_code = loc_dom.xpath('//input[contains(@name, "Zip")]/@value')[0]
            phone = loc_dom.xpath('//input[contains(@name, "Phone")]/@value')[0]
            latitude = loc_dom.xpath('//input[contains(@name, "Latitude")]/@value')[0]
            longitude = loc_dom.xpath('//input[contains(@name, "Longitude")]/@value')[0]

            item = SgRecord(
                locator_domain=domain,
                page_url="https://pmi-parking.com/r/parking/home.aspx",
                location_name="",
                street_address=poi["Address"],
                city=poi["City"],
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
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
