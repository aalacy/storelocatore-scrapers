from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "toyota.astra.co.id"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "authorization",
    }
    session.request(
        "https://ilm.toyota-emc.tech/api/v1/provinces", method="OPTIONS", headers=hdr
    )
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Authorization": "Bearer j8AV9INIchSsX1CFFD4T5vo6LyH9RUWukFsakQYpH0V8k2pMXnkX8NKtZURp",
    }
    provinces = session.get(
        "https://ilm.toyota-emc.tech/api/v1/provinces", headers=hdr
    ).json()
    for p in provinces:
        url = f"https://ilm.toyota-emc.tech/api/v1/cities?province_id={p['id']}"
        cities = session.get(url, headers=hdr).json()
        for c in cities:
            url = f"https://ilm.toyota-emc.tech/api/v1/dealers?field=all&city_id={c['id']}"
            hdr = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Authorization": "Bearer j8AV9INIchSsX1CFFD4T5vo6LyH9RUWukFsakQYpH0V8k2pMXnkX8NKtZURp",
                "Origin": "https://www.toyota.astra.co.id",
                "Connection": "keep-alive",
                "Referer": "https://www.toyota.astra.co.id/",
            }

            all_locations = session.get(url, headers=hdr).json()
            for poi in all_locations:
                latitude = poi["lat"] if poi["lat"] != "0" else ""
                longitude = poi["lng"] if poi["lng"] != "0" else ""

                item = SgRecord(
                    locator_domain=domain,
                    page_url=poi["website"],
                    location_name=poi["name"],
                    street_address=poi["address"],
                    city=poi["city_name"],
                    state=poi["province"]["name"],
                    zip_postal="",
                    country_code="Indonesia",
                    store_number=poi["id"],
                    phone=poi["phone"],
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
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
