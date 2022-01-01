import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.columbiasportswear.ie"
    api_url = "https://www.columbiasportswear.ie/IE/l/stores/"
    with SgRequests() as http:
        r = http.get(url=api_url)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath("//p[./strong]")
        for d in div:

            page_url = "https://www.columbiasportswear.ie/IE/l/stores/"
            location_name = "".join(d.xpath(".//strong/text()"))
            street_address = "".join(d.xpath("./text()[1]")).replace("\n", "").strip()
            postal = "".join(d.xpath("./text()[3]")).replace("\n", "").strip()
            country_code = "IE"
            city = (
                "".join(d.xpath("./text()[2]"))
                .replace("\n", "")
                .replace("2.", "")
                .strip()
            )
            phone = (
                "".join(d.xpath("./text()[4]"))
                .replace("\n", "")
                .replace("Tel:", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(d.xpath("./text()"))
                .replace("\n", "")
                .split("Opening Hours:")[1]
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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
