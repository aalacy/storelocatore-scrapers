from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.mcdonalds.ru/api/restaurants"
    domain = "mcdonalds.ru"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr).json()

    all_locations = response["restaurants"]
    for loc in all_locations:
        poi = session.get(f'https://mcdonalds.ru/api/restaurant/{loc["id"]}').json()[
            "restaurant"
        ]
        street_address = poi["address"]
        city = poi["city"]
        street_address = street_address.split(city)[-1].strip()
        if street_address.startswith(","):
            street_address = street_address[1:].strip()
        hoo = []
        for day, hours in poi["lobbyOpeningHours"].items():
            if type(hours) != list or not hours:
                continue
            hoo.append(f'{day} {hours[0]["name"]}')
        hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://mcdonalds.ru/restaurants/map",
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=poi["region"],
            zip_postal=SgRecord.MISSING,
            country_code="RU",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type=SgRecord.MISSING,
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hours_of_operation,
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
