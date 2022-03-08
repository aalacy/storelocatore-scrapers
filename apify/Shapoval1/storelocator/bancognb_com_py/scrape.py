from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bancognb.com.py/"
    api_url = "https://www.bancognb.com.py/main/oficinas#!"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="selectCiudades"]/a')
    for d in div:
        slug = "".join(d.xpath(".//text()"))
        r = session.get(f"https://www.bancognb.com.py/main/oficinas?ciudad={slug}")
        js = r.json()
        for j in js:

            page_url = "https://www.bancognb.com.py/main/oficinas"
            location_name = (
                "".join(j.get("nombre")).replace("\n", "").strip() or "<MISSING>"
            )
            ad = "".join(j.get("direccion")).replace("\n", "").strip() or "<MISSING>"
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            city = a.city or "<MISSING>"
            if street_address == "<MISSING>" or street_address.isdigit():
                street_address = ad
            state = slug
            postal = "<MISSING>"
            country_code = "PY"
            location_type = j.get("tipo") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            if latitude == "=B1":
                latitude = "<MISSING>"
            longitude = j.get("lon") or "<MISSING>"
            phone = j.get("telefonos") or "<MISSING>"
            hours_of_operation = "<MISSING>"
            hours = j.get("horarios")
            if hours:
                h = html.fromstring(hours)
                hours_of_operation = " ".join(h.xpath("//*//text()"))
                hours_of_operation = " ".join(hours_of_operation.split())

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
