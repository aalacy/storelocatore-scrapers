from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://lukeslocker.com/"
    page_url = "https://lukeslocker.com/pages/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//image-with-text-item")
    for d in div:

        location_name = "".join(d.xpath(".//h2//text()")).replace("\n", "").strip()
        ad = "".join(d.xpath(".//h3/following-sibling::div[1]/p[2]/text()"))
        street_address = ad.split(",")[0].strip()
        if ad.count(",") > 2:
            street_address = ad.split(",")[1].strip()

        state = ad.split(",")[-1].split()[0].strip()
        postal = ad.split(",")[-1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[-2].strip()
        phone = (
            "".join(
                d.xpath(
                    './/strong[contains(text(), "Phone:")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath(".//h3/following-sibling::div[1]/p[last()]//text()"))
            .replace("\n", "")
            .strip()
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
