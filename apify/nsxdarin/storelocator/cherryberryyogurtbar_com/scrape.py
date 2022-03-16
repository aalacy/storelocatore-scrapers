import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cherryberryyogurtbar.com/"
    api_url = "https://www.cherryberryyogurtbar.com/find-a-location"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "markers")]/text()'))
        .split('"markers":')[1]
        .split("]")[0]
        + "]"
    )
    js = json.loads(div)

    for j in js:

        info = j.get("text")
        a = html.fromstring(info)
        page_url = "https://www.cherryberryyogurtbar.com/find-a-location"
        location_name = j.get("title") or "<MISSING>"
        street_address = (
            "".join(a.xpath('//span[@itemprop="streetAddress"]/text()')) or "<MISSING>"
        )
        state = (
            "".join(a.xpath('//span[@itemprop="addressRegion"]/text()')) or "<MISSING>"
        )
        postal = (
            "".join(a.xpath('//span[@itemprop="postalCode"]/text()')) or "<MISSING>"
        )
        country_code = "CA"
        if postal.isdigit():
            country_code = "US"
        city = (
            "".join(a.xpath('//span[@itemprop="addressLocality"]/text()'))
            or "<MISSING>"
        )
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = (
            "".join(
                a.xpath(
                    '//div[@class="views-field views-field-field-phone"]/div[1]/text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = "<MISSING>"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
