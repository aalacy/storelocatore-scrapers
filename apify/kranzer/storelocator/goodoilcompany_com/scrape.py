from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://goodoilcompany.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://goodoilcompany.com",
        "Connection": "keep-alive",
        "Referer": "https://goodoilcompany.com/locations",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    cookies = {
        "exp_csrf_token": "8e36579b51a1ea6ab3033c171e9be79afd79b724",
    }
    data = {"city": "", "XID": "8e36579b51a1ea6ab3033c171e9be79afd79b724"}

    r = session.post(
        "https://goodoilcompany.com/deal-signup/filter",
        headers=headers,
        data=data,
        cookies=cookies,
    )

    div = r.text.split("|")
    div = list(filter(None, [a.strip() for a in div]))
    for d in div:

        page_url = "https://goodoilcompany.com/locations"
        location_name = d.split("+")[0].strip()
        street_address = d.split("+")[2].strip()
        state = d.split("+")[4].strip()
        postal = d.split("+")[5].strip()
        country_code = "US"
        city = d.split("+")[3].strip()
        store_number = location_name.split("#")[1].strip()
        latitude = d.split("+")[7].strip()
        longitude = d.split("+")[6].strip()
        if location_name == "Medaryville #60" or location_name == "North Judson #50":
            longitude = d.split("+")[7].strip()
            latitude = d.split("+")[6].strip()

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
