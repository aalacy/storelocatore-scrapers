import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chilis.qa"
    api_url = "https://chilis.qa/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "places")]/text()'))
        .split('"places":')[1]
        .split(',"map_options"')[0]
        .strip()
    )
    js = json.loads(div)
    for j in js:

        a = j.get("location")
        page_url = "https://chilis.qa/locations/"
        location_name = j.get("title") or "<MISSING>"
        info = (
            "".join(j.get("content"))
            .replace("\r\n", " ")
            .replace("44683356", "4468 3356")
            .replace("44146943", "4414 6943")
            .strip()
        )
        phone = " ".join(info.split()[-2:]).strip()
        street_address = (
            info.replace(f"{phone}", "")
            .replace("Chilli's Restaurant", "")
            .replace("Chili's Restaurant", "")
            .replace(", E", "E")
            .replace(", Doha, Qatar", "")
            .strip()
        )
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal_code") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        latitude = a.get("lat") or "<MISSING>"
        longitude = a.get("lng") or "<MISSING>"

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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
