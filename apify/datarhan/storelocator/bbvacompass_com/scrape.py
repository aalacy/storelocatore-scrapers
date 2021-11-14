from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bbvausa.com"
    start_url = "https://apps.pnc.com/locator-api/locator/api/v1/locator/browse"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-App-Key": "pyHnMuBXUM1p4AovfkjYraAJp6",
        "Origin": "https://apps.pnc.com",
    }
    data = session.get(start_url, headers=hdr).json()
    for state, state_data in data.items():
        for p in state_data["locations"]:
            for e in p["locationDetails"]:
                poi_url = f'https://apps.pnc.com/locator-api/locator/api/v2/location/details/{e["externalId"]}'
                poi = session.get(poi_url, headers=hdr)
                code = poi.status_code
                while code != 200:
                    session = SgRequests()
                    poi = session.get(poi_url, headers=hdr)
                    code = poi.status_code
                poi = poi.json()
                page_url = f'https://apps.pnc.com/locator/location-details/{poi["address"]["county"]}/{poi["address"]["city"]}/{poi["slsNumber"]}/{poi["externalId"]}/{poi["address"]["city"]}'
                street_address = poi["address"]["address1"]
                if poi["address"]["address2"]:
                    street_address += ", " + poi["address"]["address2"]
                phone = [
                    e["contactInfo"]
                    for e in poi["contactInfo"]
                    if e["contactType"] == "Internal Phone"
                ]
                phone = phone[0] if phone else ""
                hoo = []
                if poi["services"][0]["hoursByDayIndex"]:
                    for e in poi["services"][0]["hoursByDayIndex"]:
                        day = e["dayName"]
                        opens = e["hours"][0]["open"]
                        if opens:
                            hoo.append(f"{day} {opens} {e['hours'][0]['close']}")
                        else:
                            hoo.append(f"{day} closed")
                hoo = " ".join(hoo)

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["locationName"],
                    street_address=street_address,
                    city=poi["address"]["city"],
                    state=poi["address"]["state"],
                    zip_postal=poi["address"]["zip"],
                    country_code="",
                    store_number=poi["locationId"],
                    phone=phone,
                    location_type=poi["locationType"]["locationTypeDesc"],
                    latitude=poi["address"]["latitude"],
                    longitude=poi["address"]["longitude"],
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
