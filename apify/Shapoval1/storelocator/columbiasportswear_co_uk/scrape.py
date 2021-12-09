import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.columbiasportswear.co.uk"
    api_url = "https://www.columbiasportswear.co.uk/l/stores"
    with SgRequests() as http:
        r = http.get(url=api_url)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath("//p[./strong]")
        for d in div:

            page_url = "https://www.columbiasportswear.co.uk/l/stores"
            location_name = "".join(d.xpath(".//strong/text()"))
            ad = " ".join(d.xpath("./text()")).replace("\n", "").split("Tel")[0].strip()
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "UK"
            city = a.city or "<MISSING>"
            phone = (
                " ".join(d.xpath("./text()"))
                .replace("\n", "")
                .split("Tel")[1]
                .split(":")[1]
                .split("Opening")[0]
                .strip()
            )
            hours_of_operation = (
                " ".join(d.xpath("./text()"))
                .replace("\n", "")
                .split("ours:")[1]
                .strip()
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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
