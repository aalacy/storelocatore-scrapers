from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch


def fetch_data():
    session = SgRequests()
    domain = "birkenstock.com"
    all_countries = {
        "US": "https://www.birkenstock.com/on/demandware.store/Sites-US-Site/en_US/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=mi&searchText=&countryCode=US&storeLocatorType=regular",
        "AT": "https://www.birkenstock.com/on/demandware.store/Sites-DE-Site/de_AT/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=km&searchText=&countryCode=AT&storeLocatorType=regular",
        "JP": "https://www.birkenstock.com/on/demandware.store/Sites-JP-Site/ja_JP/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=mi&searchText=&countryCode=JP&storeLocatorType=regular",
        "DK": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/da_DK/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=km&searchText=&countryCode=DK&storeLocatorType=regular",
        "GB": "https://www.birkenstock.com/on/demandware.store/Sites-GB-Site/en_GB/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=km&searchText=&countryCode=GB&storeLocatorType=regular",
        "DE": "https://www.birkenstock.com/on/demandware.store/Sites-DE-Site/de_DE/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=km&searchText=&countryCode=DE&storeLocatorType=regular",
        "IT": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/it_IT/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=km&searchText=&countryCode=IT&storeLocatorType=regular",
        "FI": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/en_FI/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=mi&searchText=&countryCode=FI&storeLocatorType=regular",
        "NL": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/nl_NL/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=km&searchText=&countryCode=NL&storeLocatorType=regular",
        "ES": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/es_ES/Stores-GetStoresJson?latitude={}&longitude={}&latituderef={}&longituderef={}&storeid=&distance=100&distanceunit=km&searchText=&countryCode=ES&storeLocatorType=regular",
    }
    for country, url in all_countries.items():
        all_coords = DynamicGeoSearch(
            country_codes=[country.lower()], expected_search_radius_miles=50
        )
        for lat, lng in all_coords:
            data = session.get(url.format(lat, lng, lat, lng)).json()
            for i, poi in data["stores"].items():
                page_url = f"https://www.birkenstock.com/{country.lower()}/storelocator"
                if country == "FI":
                    page_url = "https://www.birkenstock.com/fi-en/storelocator"
                street_address = poi["address1"]
                if poi["address2"]:
                    street_address += ", " + poi["address2"]
                hoo = ""
                if poi.get("storeHoursHTML"):
                    hoo_data = etree.HTML(poi["storeHoursHTML"]).xpath("//li/text()")
                    days = hoo_data[:7]
                    hours = hoo_data[7:]
                    hoo = list(map(lambda d, h: d + " " + h, days, hours))
                    hoo = " ".join(hoo)

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=street_address,
                    city=poi["city"],
                    state=poi["state"],
                    zip_postal=poi["postalCode"],
                    country_code=poi["countryCode"],
                    store_number=poi["id"],
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
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
