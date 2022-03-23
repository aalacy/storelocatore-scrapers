from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jumbo.cl"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.jumbo.cl/",
        "x-api-key": "IuimuMneIKJd3tapno2Ag1c1WcAES97j",
        "Content-Type": "application/json",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "Origin": "https://www.jumbo.cl",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive",
    }

    r = session.get(
        "https://apijumboweb.smdigital.cl/cms/api/v1/json/cms/page-22134.json",
        headers=headers,
    )
    js = r.json()["acf"]["localities"]
    for j in js:

        page_url = "https://www.jumbo.cl/locales"
        location_name = j.get("name") or "<MISSING>"
        ad = j.get("address") or "<MISSING>"
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = j.get("regions") or "<MISSING>"
        country_code = "CL"
        city = j.get("cities") or "<MISSING>"
        geo = "".join(j.get("geolocation"))
        latitude = geo.split(",")[0].strip()
        longitude = geo.split(",")[1].strip()
        hours_of_operation = (
            "".join(j.get("schedule"))
            .replace("\r", " ")
            .replace("\n", " ")
            .replace("<br /> ", " ")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
