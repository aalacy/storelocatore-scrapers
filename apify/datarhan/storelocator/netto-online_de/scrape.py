# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_1_KM


def fetch_data():
    session = SgRequests()

    start_url = "https://www.netto-online.de/INTERSHOP/web/WFS/Plus-NettoDE-Site/de_DE/-/EUR/ViewNettoStoreFinder-GetStoreItems"
    domain = "netto-online.de"
    hdr = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.GERMANY],
        expected_search_radius_miles=1,
        granularity=Grain_1_KM(),
    )
    for lat, lng in all_coords:
        frm = f"s={lat}&n={lat + 0.35}&w={lng}&e={lng + 0.45}&netto=false&city=false&service=false&beverage=false&nonfood=false"
        all_locations = session.post(start_url, data=frm, headers=hdr).json()
        for poi in all_locations["store_items"]:
            hoo = etree.HTML(poi["store_opening"]).xpath("//text()")
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.netto-online.de/filialfinder",
                location_name=poi["store_name"],
                street_address=poi["street"],
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["post_code"],
                country_code="DE",
                store_number=poi["store_id"],
                phone="",
                location_type="",
                latitude=poi["coord_latitude"],
                longitude=poi["coord_longitude"],
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
