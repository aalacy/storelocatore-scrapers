from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.acurapr.com/"
    api_url = "https://www.acurapr.com/dealers"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-12"]')
    for d in div:

        page_url = "https://www.acurapr.com/dealers"
        location_name = "".join(d.xpath(".//h1//text()")).replace("\n", "").strip()
        ad = "".join(d.xpath(".//h1/following::p[1]/span/text()[1]"))
        street_address = ad.split(",")[0].strip()
        postal = ad.split(",")[2].strip()
        country_code = "PR"
        city = ad.split(",")[1].strip()
        phone = (
            "".join(d.xpath(".//h1/following::p[1]/span/text()[2]"))
            .replace("\n", "")
            .split("/")[0]
            .replace("Sales:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath(".//h1/following::p[2]/span/text()"))
            .replace("\n", "")
            .strip()
        )

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
