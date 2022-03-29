from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "birkenstock.com"
    all_countries = {
        "US": "https://www.birkenstock.com/on/demandware.store/Sites-US-Site/en_US/Stores-GetStoresJson?latitude=40.724351&longitude=-74.001120&latituderef=40.724351&longituderef=-74.001120&storeid=&distance=19&distanceunit=mi&searchText=&countryCode=US&storeLocatorType=regular",
        "AT": "https://www.birkenstock.com/on/demandware.store/Sites-DE-Site/de_AT/Stores-GetStoresJson?latitude=47.546332&longitude=14.257807&latituderef=47.546332&longituderef=14.257807&storeid=&distance=251&distanceunit=km&searchText=&countryCode=AT&storeLocatorType=regular",
        "JP": "https://www.birkenstock.com/on/demandware.store/Sites-JP-Site/ja_JP/Stores-GetStoresJson?latitude=35.667625&longitude=139.705414&latituderef=35.667625&longituderef=139.705414&storeid=&distance=188&distanceunit=mi&searchText=&countryCode=JP&storeLocatorType=regular",
        "DK": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/da_DK/Stores-GetStoresJson?latitude=55.6808997&longitude=12.5774679&latituderef=55.6808997&longituderef=12.5774679&storeid=&distance=420&distanceunit=km&searchText=&countryCode=DK&storeLocatorType=regular",
        "GB": "https://www.birkenstock.com/on/demandware.store/Sites-GB-Site/en_GB/Stores-GetStoresJson?latitude=51.521723&longitude=-0.128385&latituderef=51.521723&longituderef=-0.128385&storeid=&distance=463&distanceunit=km&searchText=&countryCode=GB&storeLocatorType=regular",
        "DE": "https://www.birkenstock.com/on/demandware.store/Sites-DE-Site/de_DE/Stores-GetStoresJson?latitude=50.721873&longitude=10.471910&latituderef=50.721873&longituderef=10.471910&storeid=&distance=118&distanceunit=km&searchText=&countryCode=DE&storeLocatorType=regular",
        "IT": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/it_IT/Stores-GetStoresJson?latitude=43.782335&longitude=11.602853&latituderef=43.782335&longituderef=11.602853&storeid=&distance=537&distanceunit=km&searchText=&countryCode=IT&storeLocatorType=regular",
        "FI": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/en_FI/Stores-GetStoresJson?latitude=60.16985569999999&longitude=24.938379&latituderef=60.16985569999999&longituderef=24.938379&storeid=&distance=115&distanceunit=mi&searchText=Helsinki&countryCode=FI&storeLocatorType=regular",
        "NL": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/nl_NL/Stores-GetStoresJson?latitude=52.099762&longitude=5.665352&latituderef=52.099762&longituderef=5.665352&storeid=&distance=457&distanceunit=km&searchText=&countryCode=NL&storeLocatorType=regular",
        "ES": "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/es_ES/Stores-GetStoresJson?latitude=40.423821&longitude=-3.704944&latituderef=40.423821&longituderef=-3.704944&storeid=&distance=567&distanceunit=km&searchText=&countryCode=ES&storeLocatorType=regular",
    }
    for country, url in all_countries.items():
        data = session.get(url).json()
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
