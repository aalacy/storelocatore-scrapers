from time import sleep
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    start_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=JVDLDVAOMOPVWDSW&center={},{}&coordinates={},{},{},{}&multi_account=false&page=1&pageSize=300"
    domain = "eggsmart.com"

    scraped_poi = []
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=200
    )
    for lat, lng in all_coords:
        all_locations = session.get(
            start_url.format(
                lat, lng, lat - 1.26259, lng + -2.20, lat + 1.2364, lng - 2.20550
            )
        ).json()
        for poi in all_locations:
            page_url = "https://locations.eggsmart.com" + poi["llp_url"]
            if page_url in scraped_poi:
                continue
            scraped_poi.append(page_url)
            street_address = poi["store_info"]["address"]
            with SgFirefox() as driver:
                driver.get(page_url)
                sleep(5)
                loc_dom = etree.HTML(driver.page_source)
            hoo = loc_dom.xpath('//div[@ng-if="hoursCardC.locHours"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            location_type = ""
            if (
                hoo
                == "Monday Closed Tuesday Closed Wednesday Closed Thursday Closed Friday Closed Saturday Closed Sunday Closed"
            ):
                location_type = "temporarily closed"

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["store_info"]["name"],
                street_address=street_address,
                city=poi["store_info"]["locality"],
                state=poi["store_info"]["region"],
                zip_postal=poi["store_info"]["postcode"],
                country_code=poi["store_info"]["country"],
                store_number="",
                phone=poi["store_info"]["phone"],
                location_type=location_type,
                latitude=poi["store_info"]["latitude"],
                longitude=poi["store_info"]["longitude"],
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
