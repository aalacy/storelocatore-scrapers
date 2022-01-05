from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.wackywarehouse.co.uk/"
    api_url = "https://www.wackywarehouse.co.uk/search/LocationsJSON"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("LocationURL")
        location_name = j.get("name")
        latitude = j.get("lat")
        longitude = j.get("lng")
        if longitude == "0":
            longitude = "<MISSING>"
        street_address = f"{j.get('HouseNumber')} {j.get('Street')}".strip()
        state = j.get("County") or "<MISSING>"
        postal = j.get("PostCode") or "<MISSING>"
        country_code = "UK"
        city = j.get("Town") or "<MISSING>"
        if city == "<MISSING>":
            city = j.get("County")
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = "<MISSING>"
        info = tree.xpath("//div[./h4]/p[1]/text()")
        info = list(filter(None, [a.strip() for a in info]))
        for i in info:
            if "Telephone" in i or "".join(i).startswith("0"):
                phone = "".join(i).replace("Telephone:", "").strip()
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//*[contains(text(), "Telephone:")]/text()'))
                .replace("Telephone:", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(
                tree.xpath('//*[text()="Opening Hours"]/following-sibling::p[1]/text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//*[./*[text()="Opening Hours"]]/following-sibling::p[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
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
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
