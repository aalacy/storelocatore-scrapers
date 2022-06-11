import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.henrystavern.com/"
    api_url = "https://www.henrystavern.com/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "locations:")]/text()'))
        .split("locations:")[1]
        .split("[]}}],")[0]
        .strip()
        + "[]}}]"
    )
    js = json.loads(div)
    for j in js:
        slug = j.get("url")
        page_url = f"https://www.henrystavern.com{slug}"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        hours = j.get("hours")
        hours_of_operation = "<MISSING>"
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//p[1]//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
