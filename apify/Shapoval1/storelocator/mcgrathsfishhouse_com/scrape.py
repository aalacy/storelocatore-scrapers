import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mcgrathsfishhouse.com/"
    api_url = "https://www.mcgrathsfishhouse.com/Directions"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        .split("dynamicData:")[1]
        .split("csrfToken")[0]
        .strip()
    )
    div = "".join(div[:-1])
    js = json.loads(div)
    for j in js["storeLocation"]["locations"]:

        page_url = "https://www.mcgrathsfishhouse.com/Directions"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours = j.get("storeHoursSummary")
        hours_of_operation = "<MISSING>"
        tmp = []
        if hours:
            for h in hours:
                day = h.get("daysSummary")
                time = h.get("hoursSummary")
                line = f"{day} {time}"
                tmp.append(line)
            hours_of_operation = " ".join(tmp)
        store_number = j.get("locationId")
        if store_number == -1:
            store_number = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
