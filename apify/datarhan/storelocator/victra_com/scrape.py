from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "victra.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    start_url = "https://victra.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=200"

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for lat, lng in all_coords:
        all_poi = session.get(start_url.format(lat, lng), headers=headers).json()
        for poi in all_poi:
            street_address = poi["address"]
            if poi["address2"]:
                street_address += " " + poi["address2"]
            hoo = ""
            if poi.get("hours"):
                hoo = etree.HTML(poi["hours"]).xpath("//text()")
                hoo = [e.strip() for e in hoo if e.strip()]
                hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["permalink"],
                location_name=poi["store"],
                street_address=street_address,
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["zip"],
                country_code=poi["country"],
                store_number=poi["id"],
                phone=poi["phone"],
                location_type=SgRecord.MISSING,
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
