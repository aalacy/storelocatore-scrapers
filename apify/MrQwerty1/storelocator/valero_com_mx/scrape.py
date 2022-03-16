from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode or ""

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://valero.com.mx/wp-content/themes/VALERO-THEME-2022/plugins/estaciones/estaciones.json"
    page_url = "https://valero.com.mx/stations-valero/?lang=en"
    r = session.get(api)
    js = r.json().values()

    for jj in js:
        for j in jj:
            location_name = j.get("name")
            raw_address = j.get("adress")
            phone = j.get("phone") or ""
            if "/" in phone:
                phone = phone.split("/")[0].strip()
            if "–" in phone:
                phone = phone.split("–")[0].strip()
            if "." in phone:
                phone = SgRecord.MISSING

            street_address, city, state, postal = get_international(raw_address)
            postal = postal.replace("C", "").replace("P", "").replace(".", "").strip()
            ll = j.get("long-lat") or ","
            latitude, longitude = ll.split(",")

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="MX",
                phone=phone,
                latitude=latitude.strip(),
                longitude=longitude.strip(),
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://valero.com.mx/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
