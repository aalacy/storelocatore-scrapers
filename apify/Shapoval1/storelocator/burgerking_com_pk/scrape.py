import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://bkdelivery.pk/"
    api_url = "https://bkdelivery.pk/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var cityData = ")]/text()'))
        .split("var cityData = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js.keys():
        city = j
        for k in js.values():
            for c in k:

                page_url = "https://bkdelivery.pk/"
                location_name = "".join(c.get("area_name")) + ", " + city
                country_code = "Pakistan"
                latitude = c.get("lat")
                longitude = c.get("lng")

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=SgRecord.MISSING,
                    city=city,
                    state=SgRecord.MISSING,
                    zip_postal=SgRecord.MISSING,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=SgRecord.MISSING,
                    location_type=SgRecord.MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
                    raw_address=location_name,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
