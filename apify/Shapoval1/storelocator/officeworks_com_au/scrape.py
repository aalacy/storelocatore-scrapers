from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.officeworks.com.au/"
    api_url = "https://www.officeworks.com.au/shop/officeworks/storepage"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//img[contains(@src, "pin")]/following-sibling::div[1]//a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.officeworks.com.au{slug}"
        store_number = page_url.split("/")[-3].strip()
        r = session.get(
            f"https://www.officeworks.com.au/catalogue-app/api/stores/{store_number}",
            headers=headers,
        )
        js = r.json()
        location_name = js.get("name")
        a = js.get("address")
        street_address = a.get("street") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postCode") or "<MISSING>"
        country_code = "AU"
        city = a.get("suburb") or "<MISSING>"
        latitude = js.get("location").get("latitude")
        longitude = js.get("location").get("longitude")
        phone = js.get("contact").get("phone")
        hours_of_operation = "<MISSING>"
        hours = js.get("openingHours")
        tmp = []
        if hours:
            for h in hours:
                days = h.get("dayOfWeek")
                opens = h.get("open")
                closes = h.get("close")
                line = f"{days} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = (
                " ;".join(tmp).replace("Closed - Closed", "Closed").strip()
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
            location_type=SgRecord.MISSING,
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
