from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.birkenstock.com/on/demandware.store/Sites-{0}-Site/en_{0}/Stores-GetStoresJson?latitude=&longitude=&latituderef=&longituderef=&storeid=&distance=&distanceunit=mi&searchText=&countryCode={0}&storeLocatorType=regular"
    domain = "birkenstock.com"
    all_countries = ["US", "AT", "JP", "DK", "GB", "DE", "IT", "FI", "NL", "ES"]
    for country in all_countries:
        url = start_url.format(country)
        if country == "AT":
            url = "https://www.birkenstock.com/on/demandware.store/Sites-DE-Site/de_AT/Stores-GetStoresJson?latitude=&longitude=&latituderef=&longituderef=&storeid=&distance=&distanceunit=mi&searchText=&countryCode=AT&storeLocatorType=regular"
        if country == "DK":
            url = "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/da_DK/Stores-GetStoresJson?latitude=&longitude=&latituderef=&longituderef=&storeid=&distance=&distanceunit=km&searchText=&countryCode=DK&storeLocatorType=regular"
        if country == "IT":
            url = "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/en_IT/Stores-GetStoresJson?latitude=&longitude=&latituderef=&longituderef=&storeid=&distance=&distanceunit=km&searchText=&countryCode=IT&storeLocatorType=regular"
        if country == "FI":
            url = "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/en_FI/Stores-GetStoresJson?latitude=&longitude=&latituderef=&longituderef=&storeid=&distance=&distanceunit=mi&searchText=&countryCode=FI&storeLocatorType=regular"
        if country == "NL":
            url = "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/en_NL/Stores-GetStoresJson?latitude=&longitude=&latituderef=&longituderef=&storeid=&distance=&distanceunit=km&searchText=&countryCode=NL&storeLocatorType=regular"
        if country == "ES":
            url = "https://www.birkenstock.com/on/demandware.store/Sites-EU-Site/es_ES/Stores-GetStoresJson?latitude=&longitude=&latituderef=&longituderef=&storeid=&distance=&distanceunit=km&searchText=&countryCode=ES&storeLocatorType=regular"
        data = session.get(url).json()
        for i, poi in data["stores"].items():
            page_url = ""
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
                store_number="",
                phone="",
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
