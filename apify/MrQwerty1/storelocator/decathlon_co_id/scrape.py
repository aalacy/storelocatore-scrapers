from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(
        tree.xpath('//script[contains(text(), "store_marker.push(")]/text()')
    ).split("store_marker.push(")[1:]
    for d in div:
        if d.find(");") != -1:
            d = d.split(");")[0].strip()
        js = eval(d)

        page_url = (
            js.get("link") or "https://www.decathlon.co.id/en/content/11-store-location"
        )
        location_name = js.get("title")
        loc_slug = str(location_name).split()[-1].upper().strip()
        ad = js.get("address")
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state
        postal = a.postcode
        city = a.city
        store_number = js.get("store_number")
        latitude = js.get("lat")
        longitude = js.get("lng")
        phone = js.get("phone")
        info = tree.xpath(
            f'//h2[contains(text(), "{loc_slug}")]/following-sibling::p[1]/text()'
        )
        tmp = []
        for i in info:
            if "00 -" in i:
                tmp.append(i)
        hours_of_operation = (
            "; ".join(tmp).replace("OPENING HOURS", "").replace(":", "").strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="ID",
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.decathlon.co.id/en/"
    api_url = "https://www.decathlon.co.id/en/content/11-store-location"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
