from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jumbo.com.ar/"
    api_url = "https://www.jumbo.com.ar/files/AR-districts.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        state = j
        for k in js[f"{j}"]:

            page_url = "https://www.jumbo.com.ar/institucional/nuestras-sucursales"
            ad = "".join(k.get("address"))
            location_name = k.get("name") or "<MISSING>"
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            postal = a.postcode or "<MISSING>"
            country_code = "AR"
            city = a.city or "<MISSING>"
            latitude = k.get("geoCoordinates")[0]
            longitude = k.get("geoCoordinates")[1]
            phone = "".join(k.get("phone"))
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            hours_of_operation = k.get("schedule")[0]
            slug = "".join(k.get("id")).replace("EX", "")
            if slug.find("-") != -1:
                slug = slug.split("-")[0].strip()
            store_number = "<MISSING>"
            if slug.isdigit():
                store_number = slug

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
