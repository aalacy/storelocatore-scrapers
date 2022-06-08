import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://shoprite.com/pharmacy"
    page_url = "https://www.shoprite.com/sm/pickup/rsid/3000/store"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "PRELOADED_STATE")]/text()'))
        .split("PRELOADED_STATE__=")[1]
        .strip()
    )
    js = json.loads(js_block)
    for j in js["stores"]["allStores"]["items"]:

        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('addressLine1')} {j.get('addressLine2') or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        state = j.get("countyProvinceState") or "<MISSING>"
        postal = j.get("postCode") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("retailerStoreId") or "<MISSING>"
        latitude = j.get("location").get("latitude") or "<MISSING>"
        longitude = j.get("location").get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = j.get("openingHours") or "<MISSING>"
        hours_of_operation = str(hours_of_operation).replace("\n", " ").strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
