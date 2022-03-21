# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://prod-orangejulius-dairyqueen.dotcmscloud.com/api/vtl/locations?country=ca&lat={}&long={}"
    domain = "orangejulius.com/en-ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        data = json.loads(response.text)
        all_locations = data["locations"]

        for poi in all_locations:
            if poi["comingSoon"]:
                continue
            store_url = "https://www.dairyqueen.com/en-ca" + poi["url"]
            loc_response = session.get(store_url)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)
            location_name = loc_dom.xpath('//div[@class="callout"]/text()')[0]
            street_address = poi["address3"]
            city = poi["city"]
            state = poi["stateProvince"]
            zip_code = poi["postalCode"]
            country_code = poi["country"]
            store_number = poi["storeNo"]
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            location_type = poi["conceptType"]
            latitude = poi["latlong"].split(",")[0]
            longitude = poi["latlong"].split(",")[-1]
            hoo = []
            if poi.get("storeHours"):
                hours = [e[2:] for e in poi["storeHours"].split(",")]
                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                hoo = list(map(lambda d, h: d + " " + h, days, hours))
            hours_of_operation = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
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
