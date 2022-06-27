import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours):
    tmp = []
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    hourss = eval(hours)
    for d in days:
        days = d
        opens = hourss.get(f"{days}").get("open_time")
        closes = hourss.get(f"{days}").get("closing_time")
        line = f"{days} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.paulandshark.com/"
    api_url = "https://www.paulandshark.com/int_int/storefinder?___from_store=rw1_en&___from_store=us_en"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "locations")]/text()'))
        .split('"locations":')[1]
        .split(',"searchBox"')[0]
    )
    js = json.loads(div)
    for j in js:

        page_url = j.get("store_url") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        street_address = "".join(j.get("address")) or "<MISSING>"
        if street_address.find("By Appointment") != -1:
            street_address = street_address.split("By Appointment")[0].strip()
        state = j.get("region") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        if postal == "." or postal == "0" or postal == "1":
            postal = "<MISSING>"
        country_code = j.get("country_id") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = "".join(j.get("telephone")) or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        phone = phone.replace("Fri-Sat", "").strip()

        hours = j.get("schedule_data") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        if (
            hours_of_operation
            == "monday  - ; tuesday  - ; wednesday  - ; thursday  - ; friday  - ; saturday  - ; sunday  - "
        ):
            hours_of_operation = "Closed"
        hours_of_operation = hours_of_operation.replace(
            "saturday  -", "saturday Closed"
        ).replace("sunday  -", "sunday Closed")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
