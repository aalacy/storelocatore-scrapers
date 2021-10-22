import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.superduperburgers.com/"
    api_url = "https://www.superduperburgers.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
    js = json.loads(jsblock)

    for j in js["subOrganization"]:

        a = j.get("address")
        page_url = j.get("hasMap")
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("@type") or "<MISSING>"
        street_address = a.get("streetAddress")
        state = a.get("addressRegion")
        postal = a.get("postalCode")
        country_code = "US"
        city = a.get("addressLocality")
        phone = j.get("telephone")

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        latitude = "".join(tree.xpath("//div/@data-gmaps-lat"))
        longitude = "".join(tree.xpath("//div/@data-gmaps-lng"))
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./strong[contains(text(), "Hours of Operation:")]]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Limited") != -1:
            hours_of_operation = hours_of_operation.split("Limited")[0].strip()
        if hours_of_operation.find("Indoor") != -1:
            hours_of_operation = hours_of_operation.split("Indoor")[0].strip()

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
