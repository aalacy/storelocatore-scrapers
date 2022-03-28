import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.carlsjr.co.nz/"
    page_url = "https://www.carlsjr.co.nz/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div[@data-block-json]]")
    for d in div:

        js_block = "".join(d.xpath("./div/@data-block-json"))
        j = json.loads(js_block)
        a = j.get("location")
        location_name = a.get("addressTitle")
        street_address = f"{a.get('addressLine1')}" or "<MISSING>"
        if street_address.find(",") != -1:
            street_address = street_address.split(",")[0].strip()
        if street_address == "<MISSING>":
            street_address = (
                "".join(d.xpath(".//div/p/text()[last() - 1]"))
                .replace("\n", "")
                .strip()
            )
        ad = f"{a.get('addressLine2')}" or "<MISSING>"
        state = "<MISSING>"
        if "".join(d.xpath(".//h3//text()")):
            state = "".join(d.xpath(".//preceding::h2[1]/text()"))
        map_link = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
        postal = "<MISSING>"
        if ad.count(",") > 1:
            postal = ad.split(",")[-1].strip()
        if postal == "<MISSING>":
            postal = map_link.split("/@")[0].split("+")[-1]
        country_code = a.get("addressCountry") or "New Zealand"
        city = (
            "".join(d.xpath(".//h3//text()"))
            or "".join(d.xpath(".//h2//text()"))
            or "<MISSING>"
        )
        if city.find("(") != -1:
            city = (
                "".join(d.xpath(".//div/p[1]/text()[last()]")).replace("\n", "").strip()
            )
        latitude = a.get("mapLat")
        longitude = a.get("mapLng")
        hours_of_operation = (
            " ".join(d.xpath(".//div/p[position()>1]//text()"))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Drive") != -1:
            hours_of_operation = hours_of_operation.split("Drive")[0].strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
