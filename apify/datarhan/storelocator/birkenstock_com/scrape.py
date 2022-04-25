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
    all_types = {
        "US": {"1": "BIRKENSTOCK STORE", "2": "Authorized Retailer"},
        "AT": {
            "1": "Store",
        },
        "JP": {"1": "ビルケンシュトックショップ", "2": "ビルケンシュトック コーナー", "5": "POP-UP SHOP"},
        "DK": {"1": "Store"},
        "GB": {"1": "Store", "2": "Outlet"},
        "DE": {"1": "Store", "2": "Outlet", "3": "Vertriebspartner"},
        "IT": {"1": "Store"},
        "FI": {},
        "NL": {"1": "Store", "3": "Verkooppartner"},
        "ES": {"1": "Store"},
    }
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
            country_codes=[country.lower()], expected_search_radius_miles=30
        )
        added = False
        for lat, lng in all_coords:
            data = session.get(url.format(lat, lng, lat, lng)).json()
            if country == "US" and not added:
                a_url = "https://www.birkenstock.com/on/demandware.store/Sites-US-Site/en_US/Stores-GetStoresJson?latitude=44.80903629923841&longitude=-2.6095184654691828&latituderef=40.724351&longituderef=-74.001120&storeid=&distance=2000&distanceunit=mi&searchText=&countryCode=US&storeLocatorType=regular"
                data_2 = session.get(a_url).json()
                data["stores"].update(data_2["stores"])
                added = True
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
                state = poi["state"]
                zip_code = poi["postalCode"]
                if len(zip_code) == 2:
                    zip_code = poi["state"]
                    state = poi["postalCode"]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=street_address,
                    city=poi["city"],
                    state=state,
                    zip_postal=zip_code,
                    country_code=poi["countryCode"],
                    store_number=poi["id"],
                    phone=poi["phone"],
                    location_type=all_types[country][str(poi["storeType"])],
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
