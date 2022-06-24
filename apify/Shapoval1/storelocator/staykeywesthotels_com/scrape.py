from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://staykeywesthotels.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://staykeywesthotels.com",
        "Connection": "keep-alive",
        "Referer": "https://staykeywesthotels.com/find-a-keywest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }

    data = {"action": "get_properties_for_map"}

    r = session.post(
        "https://staykeywesthotels.com/wp-admin/admin-ajax.php",
        headers=headers,
        data=data,
    )
    js = r.json()
    for j in js.values():
        b = j.get("properties")
        for a in b.values():

            page_url = a.get("link")
            location_type = a.get("type")
            ad = "".join(a.get("address_full"))
            street_address = a.get("address")
            state = a.get("state_abbr")
            postal = ad.split()[-1].strip()
            country_code = "US"
            city = a.get("city")
            location_name = f"{city}, {a.get('state')}"
            store_number = a.get("id")
            latitude = a.get("latitude")
            longitude = a.get("longitude")
            phone = a.get("phone")
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                "".join(
                    tree.xpath('//span[contains(text(), "Check In:")]/text()')
                ).replace("Check In:", "")
                + " - "
                + "".join(
                    tree.xpath('//span[contains(text(), "Check Out:")]/text()')
                ).replace("Check Out:", "")
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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
