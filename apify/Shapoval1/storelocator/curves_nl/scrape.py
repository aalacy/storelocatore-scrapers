from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://curves.nl"
    api_url = "https://curves.nl/wp-admin/admin-ajax.php?action=store_search&lat=52.13263&lng=5.29127&max_results=25&search_radius=10&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        slug = j.get("url")
        page_url = f"https://curves.nl{slug}"
        location_name = j.get("store")
        street_address = j.get("address")
        state = "<MISSING>"
        postal = "".join(j.get("zip"))
        if postal.find(" ") != -1:
            state = postal.split()[1].strip()
            postal = postal.split()[0].strip()
        country_code = "Netherlands"
        city = j.get("city")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        hours = j.get("hours") or "<MISSING>"
        a = html.fromstring(hours)
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
                or "<MISSING>"
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
            raw_address=f"{street_address} {city},{state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
