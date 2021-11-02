from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://aeropostalemexico.mx"
    api_url = "https://aeropostalemexico.mx/newmapa/data/dataShopBoutique.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://aeropostalemexico.mx/boutiques/"
        location_name = "".join(j.get("title")).replace("\n", "").strip()
        street_address = "".join(j.get("street")).replace("\n", " ").strip()
        street_address = " ".join(street_address.split())
        state = j.get("state")
        postal = (
            "".join(j.get("postal_code")).replace("C.P.", "").strip() or "<MISSING>"
        )
        country_code = "MX"
        city = j.get("city")
        phone = "".join(j.get("phone")).replace("\n", "").strip() or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        r = session.get(
            "https://aeropostalemexico.mx/newmapa/js/scripts_boutiques.js",
            headers=headers,
        )

        hours_of_operation = (
            r.text.split('<img src="img/icon-calendar.png">')[1]
            .split("<span>")[1]
            .split("<")[0]
            .strip()
            + " "
            + r.text.split('<img src="img/icon-clock.png">')[1]
            .split("<span>")[1]
            .split("<")[0]
            .strip()
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
