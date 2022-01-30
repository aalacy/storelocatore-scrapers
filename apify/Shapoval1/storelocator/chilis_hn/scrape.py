import ssl
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chilis.hn"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "no-cache, max-age=0",
        "Pragma": "no-cache",
        "Expires": "Tue, 01 Jan 2030 00:00:00 GMT",
        "Content-Type": "application/json",
        "Origin": "https://chilis.hn",
        "Connection": "keep-alive",
        "Referer": "https://chilis.hn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
    }
    data = '{"business_partner":7}'

    r = session.post(
        "https://www.com1dav1rtual.com/api/em/store/get_filter",
        headers=headers,
        data=data,
    )
    js = r.json()
    for j in js:

        page_url = "https://chilis.hn/informacion-restaurantes"
        location_name = j.get("name")
        street_address = j.get("address")
        country_code = j.get("country_name")
        city = "".join(j.get("location_two_name")).replace("D.C.", "").strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = (
            "".join(j.get("general_range_hour")[0].get("name"))
            .replace(" ", " - ")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
    session = SgRequests(verify_ssl=False)
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
