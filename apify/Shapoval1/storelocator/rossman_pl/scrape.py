import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.rossmann.pl/"
    api_url = "https://www.rossmann.pl/drogerie"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "props")]/text()'))
        .split('"shops":{"all":{"data":')[1]
        .split(',"fetching":false,')[0]
        .strip()
    )
    js = json.loads(div)
    for j in js:
        slug = j.get("navigateUrl")
        page_url = f"https://www.rossmann.pl/drogerie{slug}"
        a = j.get("address")
        street_address = "".join(a.get("street"))
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        postal = a.get("postCode")
        state = j.get("regionName") or "<MISSING>"
        country_code = "PL"
        city = a.get("city")
        store_number = j.get("shopNumber")
        latitude = j.get("shopLocation").get("latitude")
        longitude = j.get("shopLocation").get("longitude")
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        for d in days:
            day = d
            opens = j.get("openHours").get(f"{d}OpenFrom")
            closes = j.get("openHours").get(f"{d}OpenTo")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"
        hours_of_operation = hours_of_operation.replace("None - None", "Closed").strip()
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
