import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("day")
        opens = h.get("from")
        closes = h.get("to")
        line = f"{day} {opens} - {closes}".replace(":00:00", ":00").strip()
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pod-point.com/"
    api_url = "https://charge.pod-point.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var podAddresses =")]/text()'))
        .split("var podAddresses =")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)
    for j in js:

        ids = j.get("id")
        api_url = f"https://charge.pod-point.com/ajax/pods/{ids}"
        aa = j.get("address")
        store_number = j.get("id")
        location_name = j.get("name")
        street_address = f"{aa.get('address1')} {aa.get('address2')}".replace(
            "- Open 06:00 to 00:00", ""
        ).strip()
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        postal = aa.get("postcode")
        country_code = aa.get("country")
        city = aa.get("town")
        latitude = j.get("location").get("lat")
        longitude = j.get("location").get("lng")
        location_type = j.get("type")
        hours_of_operation = "<MISSING>"
        hours = j.get("opening").get("times") or "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        r = session.get(api_url, headers=headers)
        try:
            j = r.json()
            a = j.get("address")
            slug = a.get("slug")
            page_url = f"https://charge.pod-point.com/address/{slug}"
        except:
            page_url = "https://charge.pod-point.com/"

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
            location_type=location_type,
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
