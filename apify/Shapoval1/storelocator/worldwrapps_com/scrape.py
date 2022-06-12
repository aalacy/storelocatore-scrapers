from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://worldwrapps.com"
    page_url = "https://worldwrapps.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./p/img]")
    for d in div:

        location_name = "".join(d.xpath(".//h3//text()"))
        info = d.xpath('.//h5[text()="Address"]/following-sibling::p[1]/a/text()')
        street_address = "".join(info[1]).replace("\r\n", "").strip()
        ad = (
            "".join(
                d.xpath(
                    './/h5[text()="Address"]/following-sibling::p[1]/a/text()[last()]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            " ".join(d.xpath('.//h5[text()="Contact"]/following-sibling::p/text()[1]'))
            .replace("\n", "")
            .replace("phone", "")
            .strip()
            or "<MISSING>"
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        hours_of_operation = (
            " ".join(d.xpath('.//h5[text()="Hours"]/following-sibling::p//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
