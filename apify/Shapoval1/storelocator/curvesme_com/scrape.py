from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://curvesme.com/"
    api_url = "https://curvesme.com/find-your-curves-middle-east/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="clubs--overview--item"]')
    for d in div:
        slug = "".join(d.xpath('.//a[text()="View details"]/@href'))
        page_url = f"https://curvesme.com{slug}"
        location_name = "".join(d.xpath(".//h3/text()"))
        ad = (
            "".join(d.xpath(".//h3/following-sibling::*[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        street_address = (
            "".join(d.xpath(".//h3/following-sibling::*[1]/text()[1]"))
            .replace("\n", "")
            .strip()
        )
        city = ad.split(",")[0].strip()
        country_code = ad.split(",")[1].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        try:
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "lat")]/text()'))
                .split('"lat":"')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "lat")]/text()'))
                .split('"lng":"')[1]
                .split('"')[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('//div[contains(text(), "Phone: ")]/span[1]/text()'))
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//table[contains(@class, "hours")]//tr/td//text()'))
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
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
