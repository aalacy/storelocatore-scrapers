# -*- coding: utf-8 -*-
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://iveco.ubiest.com/oldApi/poi/search/jsonp?idcust=1124.5.6fimsa&domain=com.ubiest.usuite.iveco.truck|pointType:[AND,sales]&radius=700000&max=250&location={},{}&callback=ubiest.util.JSONP.callback&callback=jQuery1113029963157446612154_1643902720205"
    domain = "iveco.com/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL, expected_search_radius_miles=500
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        data = response.text.split("callback(")[-1][:-2]
        data = json.loads(data)
        if not data["results"]:
            continue
        for poi in data["results"]:
            poi = poi["poi"]
            street_address = poi["additional_information"].get("display_address")
            city = [
                e["short_name"]
                for e in poi["address_components"]
                if "locality" in e["types"]
            ]
            city = city[0].split("(")[0].strip() if city else ""
            state = [
                e["short_name"]
                for e in poi["address_components"]
                if "administrative_area_level_1" in e["types"]
            ]
            state = state[0] if state else ""
            zip_code = [
                e["short_name"]
                for e in poi["address_components"]
                if "postal_code" in e["types"]
            ]
            zip_code = zip_code[0] if zip_code else ""
            country_code = [
                e["short_name"]
                for e in poi["address_components"]
                if "country" in e["types"]
            ][0]
            page_url = "https://private.iveco.com/Pages/dealer_locator.html?language=en&country=uk"

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=poi["id"],
                phone=poi["formatted_phone_number"],
                location_type=poi["additional_information"]["network_type"],
                latitude=poi["geometry"]["location"]["lat"],
                longitude=poi["geometry"]["location"]["lon"],
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
