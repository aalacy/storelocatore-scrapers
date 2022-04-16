import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://o-tacos.com/"
    api_url = "https://o-tacos.com/en/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "window.locations =")]/text()'))
        .split("window.locations =")[2]
        .split(";")[0]
        .strip()
    )
    js_block = json.loads(div)
    st_js_block = str(js_block)
    js = json.loads(st_js_block)

    for j in js:

        page_url = "https://o-tacos.com/en/locations"
        try:
            a = j.get("contactInfo")[0]
        except:
            a = {}
        street_address, city, postal, country_code = (
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            "FR",
        )
        if a:
            street_address = a.get("street") or "<MISSING>"
            postal = a.get("zip") or "<MISSING>"
            country_code = a.get("country") or "<MISSING>"
            city = a.get("city") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("openingHours")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("day")
                times = h.get("hours")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = (
                "; ".join(tmp).replace("; Lundi", "Lundi").strip() or "<MISSING>"
            )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
