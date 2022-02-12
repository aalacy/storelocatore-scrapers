import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.columbiasportswear.de"
    api_url = "https://www.columbiasportswear.de/DE/l/stores"
    with SgRequests() as http:
        r = http.get(url=api_url)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath("//p[./strong]")
        for d in div:

            page_url = "https://www.columbiasportswear.de/DE/l/stores"
            location_name = "".join(d.xpath("./strong/text()"))
            ad = (
                " ".join(d.xpath("./text()"))
                .replace("\n", "")
                .split("Telefon")[0]
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "DE"
            city = a.city or "<MISSING>"
            info = d.xpath("./text()")
            phone = "<MISSING>"
            for i in info:
                if "Telefon" in i:
                    phone = str(i).strip()
                    if phone.find(":") != -1:
                        phone = phone.split(":")[1].strip()

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
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
