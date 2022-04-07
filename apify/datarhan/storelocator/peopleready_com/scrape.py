import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "peopleready.com"
    start_url = "https://www.peopleready.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=25&search_radius=100&autoload=1"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        expected_search_radius_miles=100,
    )

    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        if not response.text:
            continue
        all_poi = json.loads(response.text)

        for poi in all_poi:
            page_url = poi["permalink"]
            loc_response = session.get(page_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi["store"]
            street_address = poi["address"]
            if poi["address2"]:
                street_address += " " + poi["address2"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["zip"]
            country_code = poi["country"]
            store_number = poi["branch_number"]
            phone = poi["phone"]
            latitude = poi["lat"]
            longitude = poi["lng"]
            hours_of_operation = loc_dom.xpath(
                '//table[@class="wpsl-opening-hours"]//text()'
            )
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else ""
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
