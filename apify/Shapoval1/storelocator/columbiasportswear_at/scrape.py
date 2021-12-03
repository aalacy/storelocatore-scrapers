from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.columbiasportswear.at"
    api_url = "https://www.columbiasportswear.at/AT/l/stores"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//p[./strong]")
    for d in div:

        page_url = "https://www.columbiasportswear.at/AT/l/stores"
        location_name = "".join(d.xpath(".//strong/text()"))
        ad = " ".join(d.xpath("./text()[position()<4]")).replace("\n", "").strip()
        street_address = ad.split(",")[0].strip()
        postal = ad.split(",")[1].split()[0].strip()
        country_code = "Austria"
        city = ad.split(",")[1].split()[1].strip()
        phone = (
            "".join(d.xpath("./text()[4]"))
            .replace("\n", "")
            .replace("Telefon", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath("./text()[position()>4]")).replace("\n", "").strip()
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
