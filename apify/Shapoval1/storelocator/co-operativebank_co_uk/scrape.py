from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.co-operativebank.co.uk/"
    api_url = (
        "https://www.co-operativebank.co.uk/help-and-support/contact-us/branch-finder/"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[./a[text()="View on a map"]]')
    for d in div:

        page_url = "https://www.co-operativebank.co.uk/help-and-support/contact-us/branch-finder/"
        location_name = "".join(
            d.xpath(".//preceding-sibling::p[./strong][2]/strong/text()")
        )
        ad = "".join(
            d.xpath(
                ".//preceding-sibling::p[./strong][2]/following-sibling::p[1]//text()"
            )
        )

        location_type = "Branch"
        street_address = ad.split(",")[0].strip()
        postal = ad.split(",")[2].strip()
        country_code = "UK"
        city = ad.split(",")[1].strip()
        try:
            latitude = (
                "".join(d.xpath(".//a/@href")).split("query=")[1].split(",")[0].strip()
            )
            longitude = (
                "".join(d.xpath(".//a/@href"))
                .split("query=")[1]
                .split(",")[1]
                .split("&")[0]
                .strip()
            )
        except:
            latitude = (
                "".join(d.xpath(".//a/@href")).split("@")[1].split(",")[0].strip()
            )
            longitude = (
                "".join(d.xpath(".//a/@href")).split("@")[1].split(",")[1].strip()
            )
        hours_of_operation = (
            " ".join(d.xpath(".//preceding-sibling::p//text()"))
            .replace("\n", "")
            .split("Opening hours")[-1]
            .replace("Wheelchair accessible", "")
            .replace("Wheelchair Accessible", "")
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
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
