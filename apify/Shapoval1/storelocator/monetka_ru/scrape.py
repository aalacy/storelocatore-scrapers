import json
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.monetka.ru/"
    api_url = "https://api-maps.yandex.ru/services/geoxml/1.2/geoxml.xml?callback=jsonp1629968688826&origin=jsapi1YMapsML&url=http%3A%2F%2Fwww.monetka.ru%2Fshops_map%2Fymlall%2FKemerovo%3Fv%3D2.2"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    jsblock = r.text.split('{"featureMembers":')[1].split(',"style":"#customStyle"},')[
        0
    ]
    js = json.loads(jsblock)
    for j in js:

        j = j.get("GeoObject")
        a = j.get("metaDataProperty").get("ShopData")[0].get("info")[0].get("value")
        page_url = "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        ad = "".join(a.get("adress"))
        b = parse_address(International_Parser(), ad)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        country_code = "RU"
        store_number = a.get("alias")
        city = b.city or "<MISSING>"
        latitude = j.get("Point")[0] or "<MISSING>"
        longitude = j.get("Point")[1] or "<MISSING>"
        hours_of_operation = (
            "".join(a.get("shedule")).replace("\r\n", " ").replace("\n", " ").strip()
            or "<MISSING>"
        )
        phone = a.get("phone") or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
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
