from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kfc-ukraine.com"
    api_url = "https://kfc-ukraine.com/restaurants"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var restaurants = ")]/text()'))
        .split("var restaurants = ")[1]
        .split("var nearest_restaurant;")[0]
        .replace("}];", "}]")
        .replace("null", "None")
        .strip()
    )
    js = eval(jsblock)

    for j in js:

        page_url = "".join(j.get("share_url")).replace("\\", "").strip()
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        country_code = j.get("country_name")
        city = j.get("city_name") or "<MISSING>"
        store_number = page_url.split("/")[-1].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = (
            f"{j.get('start_time')} - {j.get('finish_time')}" or "<MISSING>"
        )
        cms = j.get("opening_soon")
        if cms == "1":
            hours_of_operation = "Coming Soon"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
