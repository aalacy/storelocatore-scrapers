from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://wsecu.org"
    api_url = "https://wsecu.org/api/locator?locationTypes=wsecu%2Catm%2Cshared&lat=47.039435&lng=-122.897605"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["locations"]
    for j in js:
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"
        if location_type == "wsecu":
            location_type = "WSECU Branche"
        if location_type == "atm":
            location_type = "ATM Location"
        if location_type == "shared":
            location_type = "Shared Branche"
        a = j.get("address")
        street_address = a.get("street") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        r = session.get(
            "https://wsecu.org/locations?wsecu=wsecu&shared=shared&atm=atm&fiatm=&deposit_taking=&surcharge_free=&coin_machine=&safe_deposit_box=&banking_kiosk=&drive-thru=&drive-thru_atm=&geo=0&a=",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        slug = "".join(tree.xpath(f'//li[@data-id="{store_number}"]/a/@href'))
        page_url = "https://wsecu.org/locations"
        if slug:
            page_url = f"https://wsecu.org{slug}"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if page_url != "https://wsecu.org/locations":
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            phone = (
                "".join(
                    tree.xpath(
                        '//div[@class="details-block html-area theme-standard desktop"]//a[contains(@href,"tel")]/text()'
                    )
                )
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath('//h2[text()="Hours"]/following-sibling::div//text()')
                )
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            cls = "".join(
                tree.xpath('//*[contains(text(),"temporarily closed")]/text()')
            )
            if cls:
                hours_of_operation = "Temporarily closed"

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
