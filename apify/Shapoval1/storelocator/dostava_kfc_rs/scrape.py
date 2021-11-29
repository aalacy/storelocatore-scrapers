import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.rs"
    api_url = "https://www.kfc.rs/restorani/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "lat")]/text()'))
        .split('"places":')[1]
        .split(',"styles"')[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:
        b = j.get("location")
        page_url = "https://www.kfc.rs/restorani/"
        location_name = j.get("title")
        info = j.get("content")
        a = html.fromstring(info)
        info = " ".join(a.xpath("//*//text()")).replace("\r\n", "").strip()
        ad = info.split("Adresa:")[1].split("telefon:")[0].strip()
        street_address = ad.split(",")[0].strip()
        state = b.get("state") or "<MISSING>"
        postal = b.get("postal_code") or "<MISSING>"
        country_code = "RS"
        city = b.get("city") or "<MISSING>"
        latitude = b.get("lat")
        longitude = b.get("lng")
        phone = info.split("telefon:")[1].split("Radno")[0].strip()
        hours_of_operation = (
            "".join(a.xpath("//strong[4]/preceding-sibling::text()[1]"))
            .replace("\n", "")
            .strip()
            + " "
            + "".join(a.xpath("//strong[4]/text()"))
        )

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
