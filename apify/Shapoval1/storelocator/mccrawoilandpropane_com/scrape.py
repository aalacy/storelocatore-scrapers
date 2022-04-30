from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://mccrawoilandpropane.com/wp-admin/admin-ajax.php?action=store_search&lat=33.53106&lng=-96.17391&max_results=25&search_radius=5000&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("permalink")
        location_name = (
            "".join(j.get("store"))
            .replace("&#8211;", "–")
            .replace("&#038;", "&")
            .strip()
        )
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        state = j.get("state")
        postal = "".join(j.get("zip"))
        if postal.find(" ") != -1:
            postal = postal.split()[1].strip()
        country_code = j.get("country")
        city = j.get("city")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        hours_of_operation = "<MISSING>"
        hours = j.get("hours") or "<MISSING>"
        if hours != "<MISSING>":
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
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
    locator_domain = "https://mccrawoilandpropane.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
