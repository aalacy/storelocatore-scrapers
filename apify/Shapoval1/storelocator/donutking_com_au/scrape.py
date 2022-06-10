from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.donutking.com.au/"
    api_url = "https://www.donutking.com.au/wp/wp-admin/admin-ajax.php?action=store_search&lat=-25.274398&lng=133.775136&max_results=500&search_radius=5000&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.donutking.com.au/stores/"
        location_name = j.get("store") or "<MISSING>"
        location_type = "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        if (
            street_address.find("PERMANENTLY CLOSED") != -1
            or street_address.find("PERMANTLY CLOSED") != -1
        ):
            continue
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        if postal == "Australia":
            postal = "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        if state == "Cannonvale":
            state = "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("hours")
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        if (
            street_address.find("TEMPORARILY CLOSED -") != -1
            or location_name.find("Temp Closed") != -1
        ):
            location_type = "Temporarily Closed"
            street_address = (
                str(street_address).replace("TEMPORARILY CLOSED -", "").strip()
            )
        if street_address.find("TEMPORARILY CLOSED") != -1:
            street_address = "<MISSING>"
            location_type = "Temporarily Closed"
        if street_address != "<MISSING>":
            b = parse_address(International_Parser(), street_address)
            street_address = (
                f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
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
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
