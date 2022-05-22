# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://schubergphilis-prod.apigee.net/prd/v2/location/locations?fields=id&fields=latitude&fields=longitude&fields=functionality&fields=audioGuidance&fields=withdrawableDenominations&fields=geldmaatPlus",
        "https://schubergphilis-prod.apigee.net/prd/v2/location/locations?fields=id&fields=latitude&fields=longitude&fields=functionality&fields=audioGuidance&fields=withdrawableDenominations&fields=geldmaatPlus&token=%7B%22id%22:%22910538%22,%22location%22:%226085001%22%7D",
        "https://schubergphilis-prod.apigee.net/prd/v2/location/locations?fields=id&fields=latitude&fields=longitude&fields=functionality&fields=audioGuidance&fields=withdrawableDenominations&fields=geldmaatPlus&token=%7B%22id%22:%22811842%22,%22location%22:%223074001%22%7D",
        "https://schubergphilis-prod.apigee.net/prd/v2/location/locations?fields=id&fields=latitude&fields=longitude&fields=functionality&fields=audioGuidance&fields=withdrawableDenominations&fields=geldmaatPlus&token=%7B%22id%22:%22914000%22,%22location%22:%226118002%22%7D",
    ]
    domain = "geldmaat.nl"
    hdr = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "schubergphilis-prod.apigee.net",
        "Origin": "https://www.locatiewijzer.geldmaat.nl",
        "Pragma": "no-cache",
        "Referer": "https://www.locatiewijzer.geldmaat.nl/",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    }
    for start_url in start_urls:
        data = session.get(start_url, headers=hdr).json()
        for poi in data["data"]:
            store_number = poi["id"]
            url = f"https://schubergphilis-prod.apigee.net/prd/v2/location/locations/{store_number}?fields=id&fields=latitude&fields=longitude&fields=functionality&fields=audioGuidance&fields=geldmaatPlus&fields=withdrawableDenominations&fields=devices&fields=city&fields=streetAddress&fields=zip&fields=depositStatus"
            poi_data = session.get(url, headers=hdr).json()
            street_address = location_name = poi_data["data"]["streetAddress"]
            for d in poi_data["data"]["devices"]:
                hoo = []
                for day, hours in d["openingHours"].items():
                    hoo.append(f"{day}: {hours[0]}")
                hoo = " ".join(hoo)

                item = SgRecord(
                    locator_domain=domain,
                    page_url="https://www.locatiewijzer.geldmaat.nl/",
                    location_name=location_name,
                    street_address=street_address,
                    city=poi_data["data"]["city"],
                    state="",
                    zip_postal=poi_data["data"]["zip"],
                    country_code="NL",
                    store_number=d["id"],
                    phone="",
                    location_type=d["functionality"],
                    latitude=poi["latitude"],
                    longitude=poi["longitude"],
                    hours_of_operation=hoo,
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
