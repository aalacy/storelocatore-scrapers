import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries, DynamicZipAndGeoSearch


def fetch_data():
    session = SgRequests()
    domain = "alphagraphics.com"
    start_url = "https://www.alphagraphics.com/agmapapi/AGLocationFinder/SearchByLocation?ParentSiteIds%5B%5D=759afee9-1554-4283-aa6c-b1e5c4a2b1de&MetroAreaName=&SearchLocation={}&Latitude={}&Longitude={}&Radius=500"
    scraped_items = []
    all_coords = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
    )
    for code, coord in all_coords:
        lat, lng = coord
        response = session.get(start_url.format(code, lat, lng))
        data = json.loads(response.text)
        if data.get("results"):
            all_locations = data["results"]

        for poi in all_locations:
            store_url = poi["url"]
            location_name = poi["title"]
            street_address = poi["addressLine1"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["zip"]
            store_number = poi["extCode"]
            phone = poi["fullAddress"].split("|")[-1]
            latitude = poi.get("lat")
            longitude = poi.get("long")

            check = "{} {}".format(location_name, street_address)
            if check in scraped_items:
                continue
            scraped_items.append(check)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath('//div[@class="location-content--time"]//text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
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
