from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tucanos.com/"
    api_url = "https://www.tucanos.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="card-body card-body-cascade"]')
    for d in div:
        res_page = "".join(d.xpath('.//a[text()="Reservations"]/@href'))
        page_url = "".join(d.xpath("./a/@href"))
        location_name = "".join(d.xpath("./a/text()"))
        street_address = (
            "".join(d.xpath("./a/following-sibling::div[1]/text()[1]"))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(d.xpath("./a/following-sibling::div[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="my-2"]//text()')).replace("\n", "").strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("Closed December 25th", "")
            .strip()
        )
        r = session.get(res_page, headers=headers)
        tree = html.fromstring(r.text)

        latitude = (
            "".join(tree.xpath('//script[contains(text(), "bizLat")]/text()'))
            .split("bizLat")[1]
            .split(",")[0]
            .replace("\\", "")
            .replace(":", "")
            .replace('"', "")
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "bizLat")]/text()'))
            .split("bizLong")[1]
            .split(",")[0]
            .replace("\\", "")
            .replace(":", "")
            .replace('"', "")
            .strip()
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
