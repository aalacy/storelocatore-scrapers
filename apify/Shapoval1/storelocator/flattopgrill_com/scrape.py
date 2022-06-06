import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.flattopgrill.com"
    page_url = "https://www.flattopgrill.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p[contains(text(), "Phone")]]')
    for d in div:

        location_name = (
            "".join(d.xpath(".//preceding::h3[1]/span//text()"))
            .replace("\n", "")
            .replace("Less", "")
            .strip()
        )
        street_address = "".join(d.xpath("./p[1]/text()")).replace("\n", "").strip()
        ad = "".join(d.xpath("./p[2]/text()")).replace("\n", "").strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = (
            "".join(d.xpath("./p[3]/text()"))
            .replace("\n", "")
            .replace("Phone.", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath("./p[./span]/following-sibling::p//text()"))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        js_block = "".join(tree.xpath("//div/@data-location"))
        js = json.loads(js_block)
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        for j in js:
            title = j.get("title")
            if title == location_name:
                latitude = j.get("Latitude") or "<MISSING>"
                longitude = j.get("Longitude") or "<MISSING>"

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
