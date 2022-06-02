import json
from lxml import etree

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "imospizza.com"
    start_url = "https://www.imospizza.com/wp-admin/admin-ajax.php"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    scraped_urls = []

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=100,
    )
    for lat, lng in all_coordinates:
        formdata = {
            "action": "get_stores",
            "lat": lat,
            "lng": lng,
            "radius": "100",
            "categories[0]": "",
        }
        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)
        for poi in data.values():
            poi_url = poi["gu"]
            if poi_url in scraped_urls:
                continue
            scraped_urls.append(poi_url)
            store_response = session.get(poi_url)
            store_dom = etree.HTML(store_response.text)
            hoo = store_dom.xpath('//div[@class="hours__store"]//text()')[1:]
            hoo = " ".join(hoo).replace("\n", "")

            item = SgRecord(
                locator_domain=domain,
                page_url=poi_url,
                location_name=poi["na"],
                street_address=poi["st"],
                city=poi["ct"],
                state=poi["rg"],
                zip_postal=poi["zp"],
                country_code="",
                store_number=poi["ID"],
                phone=poi["te"],
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lng"],
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
