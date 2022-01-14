import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.vm.co.mz/en/Individual/Support/Addresses/Find-a-Store"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    coords = dict()
    text = "".join(tree.xpath("//script[contains(text(), 'var LocsA =')]/text()"))
    text = text.split("var LocsA =")[1].split("new Maplace")[0].strip()[:-1]
    js = json5.loads(text)
    for j in js:
        title = j.get("title")
        lat = j.get("lat")
        lng = j.get("lon")
        coords[title] = {"lat": lat, "lng": lng}

    divs = tree.xpath("//table//tr[not(./td/p/strong)]")
    state = ""
    for d in divs:
        if len(d.xpath("./td")) == 4:
            state = "".join(d.xpath("./td[1]//text()")).strip()
            location_name = "".join(d.xpath("./td[2]//text()")).strip()
            hours_of_operation = "".join(d.xpath("./td[3]//text()")).strip()
            street_address = "".join(d.xpath("./td[4]//text()")).strip()
        else:
            location_name = "".join(d.xpath("./td[1]//text()")).strip()
            hours_of_operation = "".join(d.xpath("./td[2]//text()")).strip()
            street_address = "".join(d.xpath("./td[3]//text()")).strip()

        j = coords.get(location_name) or {}
        latitude = j.get("lat")
        longitude = j.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            state=state,
            country_code="MZ",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vm.co.mz/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
