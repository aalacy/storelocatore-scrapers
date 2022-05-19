import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "jlindeberg.com"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.get("https://www.jlindeberg.com/es/es/stores")
    dom = etree.HTML(response.text)
    countries = dom.xpath('//select[@name="country"]/option/@value')
    for country_code in countries:
        url = "https://www.jlindeberg.com/on/demandware.store/Sites-BSE-South-Site/en_GB/Stores-GetCities?countryCode={}&brandCode=jl".format(
            country_code
        )
        response = session.get(url, headers=headers)
        data = json.loads(response.text)
        for city in data:
            final_url = "https://www.jlindeberg.com/on/demandware.store/Sites-BSE-South-Site/en_GB/PickupLocation-GetLocations?countryCode={}&brandCode=jl&postalCodeCity={}&serviceID=SDSStores&filterByClickNCollect=false"
            final_url = final_url.format(country_code, city)
            city_response = session.get(final_url, headers=headers)
            locations = json.loads(city_response.text)
            if not locations.get("locations"):
                continue
            for poi in locations["locations"]:
                store_url = "https://www.jlindeberg.com/gb/en/stores"
                location_name = poi["storeName"]
                street_address = poi["address1"]
                state = poi.get("state")
                zip_code = poi["postalCode"]
                store_number = poi["storeID"]
                phone = poi["phone"]
                latitude = poi["latitude"]
                longitude = poi["longitude"]
                if city == "Abbotsford" and not zip_code:
                    continue

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
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation="",
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
