from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://boloco.com/"
    page_url = "https://boloco.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//span[text()="order now"]')
    for d in div:

        location_name = "".join(d.xpath(".//preceding::h2[1]//text()"))
        ad = "".join(d.xpath(".//preceding::h2[1]/following::p[1]/text()[1]"))
        street_address = " ".join(ad.split(",")[0].split()[:-1]).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].split()[-1].strip()
        phone = (
            "".join(d.xpath(".//preceding::h2[1]/following::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath(".//preceding::p[1]//text()")).replace("\n", "").strip()
        )
        tmp_cls = (
            " ".join(d.xpath(".//preceding::p[2]//text()")).replace("\n", "").strip()
        )
        if "hibernating" in tmp_cls:
            hours_of_operation = "Temporarily Closed"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
