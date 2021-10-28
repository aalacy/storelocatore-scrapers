from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data():
    session = SgRequests()
    domain = "katespade.com"
    start_url = "https://www.katespade.co.uk/on/demandware.store/Sites-ksEuUk-Site/en_GB/Stores-GetNearestStores?latitude={}&longitude={}&countryCode=&distanceUnit=mi&maxdistance=500"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL, expected_search_radius_miles=500
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng), headers=hdr).json()
        for store_number, poi in data["stores"].items():
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            poi_html = etree.HTML(poi["storeHours"])
            hoo = [e.strip() for e in poi_html.xpath("//text()") if e.strip()]
            hoo = " ".join(hoo).split("your safety")[0].split("is open:")[-1].strip()

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["storeURL"],
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state="",
                zip_postal=poi["postalCode"],
                country_code=poi["countryCode"],
                store_number=store_number,
                phone=poi["phone"],
                location_type=poi["storeType"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
