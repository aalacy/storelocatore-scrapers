from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://snclubs.com/"
    api_url = "https://www.fitnessworld.ca/wp-json/avid/v1/alllocations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        slug = j.get("loc_permalink")
        page_url = f"https://www.fitnessworld.ca/locations/{slug}/"
        location_name = j.get("loc_name")
        street_address = j.get("loc_address")
        state = j.get("loc_province")
        postal = j.get("loc_postcode")
        country_code = "CA"
        city = j.get("loc_city")
        store_number = j.get("loc_code")
        latitude = j.get("loc_latitude")
        longitude = j.get("loc_longitude")
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = "".join(tree.xpath('//a[@class="phone"]/text()')) or "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="opening-hours"]//div//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
