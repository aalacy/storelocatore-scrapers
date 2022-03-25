from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.curves.co.jp/"
    api_url = "https://www.curves.co.jp/search/shops.json?d=20220124"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        slug = j.get("url")
        page_url = f"https://www.curves.co.jp{slug}"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        state = j.get("pref") or "<MISSING>"
        country_code = "JP"
        city = j.get("city") or "<MISSING>"
        phone = j.get("tel") or "<MISSING>"
        hours_of_operation = (
            "".join(j.get("bizhour")).replace("<br>", " ").strip() or "<MISSING>"
        )
        store_number = page_url.split("/")[-1].split(".")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
