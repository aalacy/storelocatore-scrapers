from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://bobs.com.br/onde-tem-bobs"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = "".join(
        tree.xpath("//script[contains(text(), 'var arr_markers')]/text()")
    ).split("var marker =")
    for t in text:
        if "marker.bindPopup" not in t:
            continue

        latitude = t.split("lat: '")[1].split("',")[0]
        longitude = t.split("lng: '")[1].split("'")[0]
        source = t.split('bindPopup("')[1].split('", {')[0]
        root = html.fromstring(source)
        location_type = root.xpath("//div[@class='marker_popup_content']/text()")[
            0
        ].strip()
        location_name = "".join(
            root.xpath(".//span[@class='marker_popup_content_title']/text()")
        ).strip()
        street_address = (
            "".join(root.xpath("//div[@class='marker_popup_content']/text()")[1:])
            .replace("None", "")
            .strip()
        )
        if street_address.endswith(","):
            street_address = street_address[:-1]
        if street_address.startswith(","):
            street_address = street_address[1:]

        if len(street_address) < 3:
            street_address = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            country_code="BR",
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://bobs.com.br/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
