import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://mcdonalds.be/"
    api_url = "https://mcdonalds.be/nl/restaurants"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var restaurants")]/text()'))
        .split("var restaurants = ")[1]
        .split("];")[0]
        .strip()
        + "]"
    )
    js = json.loads(jsblock)
    for j in js:
        slug = j.get("slug")
        page_url = f"https://mcdonalds.be/nl/restaurants/{slug}"
        location_name = "".join(j.get("name"))
        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()
        street_address = (
            "".join(j.get("street_en")) + " " + "".join(j.get("nr")) or "<MISSING>"
        )
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "Belgium"
        city = j.get("city_en") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = "".join(j.get("lat_times_a_million"))
        latitude = latitude[:2] + "." + latitude[2:]
        longitude = "".join(j.get("lng_times_a_million"))
        longitude = longitude[:1] + "." + longitude[1:]
        phone = j.get("phone") or "<MISSING>"
        hourss = j.get("opening_hours_en")
        a = html.fromstring(hourss)
        cms = " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
        hours_of_operation = j.get("opening_hours_en")
        a = html.fromstring(hours_of_operation)
        hours_of_operation = " ".join(a.xpath("//*//text()")).replace("\n", "").strip()

        if (
            cms.find("Opening Soon") != -1
            or cms.find("OPENING SOON") != -1
            or cms.find("Opening soon") != -1
        ):
            hours_of_operation = "Coming Soon"

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
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
