import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://www.columbiasportswear.nl"
        api_url = "https://www.columbiasportswear.nl/NL/l/stores"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath("//p[./strong]")
        for d in div:

            page_url = "https://www.columbiasportswear.nl/NL/l/stores"
            location_name = "".join(d.xpath(".//strong/text()"))
            ad = (
                " ".join(d.xpath("./text()"))
                .replace("\n", "")
                .split("Tel")[0]
                .replace("The Netherlands", "")
                .strip()
            )
            address = d.xpath("./text()")
            street_address = "".join(address[1]).replace("\n", "").strip()
            if len(address) == 10:
                street_address = " ".join(address[1:3]).replace("\n", "").strip()
            postal = " ".join(ad.split()[-3:-2]).strip()
            state = ad.split()[-2].strip()
            country_code = "NL"
            city = ad.split()[-1].strip()
            phone = (
                " ".join(d.xpath("./text()"))
                .replace("\n", "")
                .split("Tel")[1]
                .split("Monday")[0]
                .replace(":", "")
                .strip()
            )
            hours_of_operation = " ".join(address[-4:]).replace("\n", "").strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
