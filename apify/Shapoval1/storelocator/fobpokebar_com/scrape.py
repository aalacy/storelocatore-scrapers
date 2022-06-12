from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://fobpokebar.com/"
    page_url = "https://fobpokebar.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p[contains(text(), "Hours")]]')
    for d in div:

        location_name = "".join(d.xpath(".//h4/text()"))
        street_address = "".join(d.xpath(".//p[1]/text()[1]")).replace(",", "").strip()
        ad = "".join(d.xpath(".//p[1]/text()[2]")).replace("\n", "").strip()
        state = ad.split()[1].strip()
        postal = ad.split()[2].strip()
        country_code = "US"
        city = ad.split()[0].strip()
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Phone#")]/text()'))
            .replace("Phone#", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//p[contains(text(), "Hours:")]/text()'))
            .replace("Hours:", "")
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
