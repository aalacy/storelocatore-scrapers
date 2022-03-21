from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://burgerking.ru/middleware/restaurants/search?latitude=55.751326&longitude=37.616425&limit=10&offset=0"
    domain = "burgerking.ru"

    all_locations = []
    data = session.get(start_url).json()
    total = data["total"]
    all_locations += data["items"]
    for i in range(9, total + 10, 9):
        data = session.get(add_or_replace_parameter(start_url, "offset", str(i))).json()
        if not data.get("items"):
            continue
        all_locations += data["items"]

    for poi in all_locations:
        addr = parse_address_intl(poi["address"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = []
        days = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье",
        ]
        for i, e in enumerate(poi["timetable"]["hall"]):
            opens = e["timeFrom"]
            closes = e["timeTill"]
            hoo.append(f"{days[i]} {opens} {closes}")
        hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://burgerking.ru/restaurants",
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal="",
            country_code=SgRecord.MISSING,
            store_number=poi["id"],
            phone=poi["phone"],
            location_type=SgRecord.MISSING,
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hours_of_operation,
            raw_address=poi["address"],
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
