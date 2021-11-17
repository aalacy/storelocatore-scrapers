from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://samsclub.com.br"
    api_url = "https://sejasocio.samsclub.com.br/wp-admin/admin-ajax.php?action=get_clubs&state=&city=&nonce=b36d7d742a"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]
    for j in js:

        page_url = "https://sejasocio.samsclub.com.br/"
        location_name = "".join(j.get("name")).replace("&#8217;", "`") or "<MISSING>"
        ad = j.get("address")
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Brazil"
        city = a.city or "<MISSING>"
        if location_name.find("Sam's Club ") != -1:
            city = location_name.replace("Sam's Club ", "").strip()
        phone = j.get("phones") or "<MISSING>"
        if "<br />" in phone:
            phone = str(phone).split("\n")[0].replace("<br />", "").strip()
        hours_of_operation = f"Weekdays {j.get('hours_week')} Saturday {j.get('hours_saturday')} Sunday {j.get('hours_sunday')}"
        if hours_of_operation == "Weekdays   Saturday   Sunday  ":
            hours_of_operation = "<MISSING>"

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests(verify_ssl=False)
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
