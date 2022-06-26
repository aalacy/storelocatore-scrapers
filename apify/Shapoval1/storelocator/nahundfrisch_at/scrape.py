from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.nahundfrisch.at/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }

    data = {
        "distance": "1500000",
        "lat": "48.2234479",
        "lng": "16.3997716",
        "service": "false",
    }

    r = session.post(
        "https://www.nahundfrisch.at/marktadmin/ajax/merchants/by_filters",
        headers=headers,
        data=data,
    )
    js = r.json()["merchants"]
    for j in js:

        location_name = j.get("name") or "<MISSING>"
        location_name = " ".join(location_name.split())
        slug = j.get("slug")
        page_url = f"https://www.nahundfrisch.at/de/kaufmann/{slug}"
        street_address = j.get("street") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "AT"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if str(phone).find("/ +43") != -1:
            phone = str(phone).split("/ +43")[0].strip()
        phone = str(phone).replace("06645826882", "").strip()
        if phone == "0":
            phone = "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="block-item-tile day"]/span//text()'))
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
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
