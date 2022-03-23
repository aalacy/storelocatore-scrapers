# -*- coding: utf-8 -*-

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.amazon.{}/location_selector/fetch_locations?longitude={}&latitude={}&clientId=amazon_{}_add_to_addressbook_mkt_mobile&countryCode={}&sortType=NEAREST&userBenefit=false&showFreeShippingLabel=false&showAvailableLocations=false"
    domain = "amazon.com/ulp"

    domains = {
        "us": "com",
        "ca": "ca",
        "gb": "co.uk",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "es": "es",
        "jp": "co.jp",
        "au": "com.au",
        "mx": "com.mx",
        "ae": "ae",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.BRITAIN,
            SearchableCountries.FRANCE,
            SearchableCountries.GERMANY,
            SearchableCountries.ITALY,
            SearchableCountries.SPAIN,
            SearchableCountries.JAPAN,
            SearchableCountries.AUSTRALIA,
            SearchableCountries.MEXICO,
            SearchableCountries.UNITED_ARAB_EMIRATES,
        ],
        expected_search_radius_miles=10,
    )
    for lat, lng in all_coords:
        c_iso = all_coords.current_country()
        url = start_url.format(domains[c_iso], lng, lat, c_iso, c_iso)
        data = session.get(url).json()

        for poi in data["locationList"]:
            street_address = poi["addressLine1"]
            if poi["addressLine2"]:
                street_address += ", " + poi["addressLine2"]
            if poi["addressLine3"]:
                street_address += ", " + poi["addressLine3"]
            hoo = []
            for e in poi["standardHours"]:
                hoo.append(f'{e["dateString"]}: {e["hoursString"]}')
            hoo = " ".join(hoo)
            zip_code = poi["postalCode"]
            if zip_code == "00000":
                zip_code = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=f"https://www.amazon.{domains[c_iso]}/ulp",
                location_name=poi["name"].split("-")[0].split("(")[0],
                street_address=street_address,
                city=poi["city"],
                state=poi["stateOrRegion"],
                zip_postal=zip_code,
                country_code=poi["countryCode"],
                store_number=poi["storeId"],
                phone="",
                location_type=poi["accessPointType"],
                latitude=poi["location"]["latitude"],
                longitude=poi["location"]["longitude"],
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
