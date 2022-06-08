import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.rejectshop.com.au/"
    page_url = "https://www.rejectshop.com.au/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath('//script[@type="application/json"]/text()'))
    js = json.loads(div)
    for j in js["props"]["pageProps"]["locations"]:

        a = j.get("address")
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("store") or "<MISSING>"
        ad = (
            f"{a.get('address_line_1')} {a.get('address_line_2')}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        b = parse_address(International_Parser(), ad)
        street_address = f"{b.street_address_1} {b.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postcode") or "<MISSING>"
        country_code = a.get("country")
        city = a.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("normal_hours")
        tmp = []
        if hours:
            for h in hours:
                days = h.get("day_of_week")
                opens = h.get("open_at")
                closes = h.get("close_at")
                line = f"{days} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{ad} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
