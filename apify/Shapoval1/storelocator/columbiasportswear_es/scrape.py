import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.columbiasportswear.es/"
    api_url = "https://www.columbiasportswear.es/ES/l/stores"
    with SgRequests() as http:
        r = http.get(url=api_url)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath(
            '//div[./div[@class="font-size-14 font-weight-bold line-height-default text-black font-open-sans"]]'
        )
        for d in div:

            page_url = "https://www.columbiasportswear.es/ES/l/stores"
            location_name = "".join(d.xpath("./div/text()"))
            ad = (
                " ".join(d.xpath("./following-sibling::div[1]/div/text()"))
                .replace("\n", "")
                .split("Teléfono")[0]
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            if street_address.find("08430") != -1:
                street_address = street_address.replace("08430", "").strip()
                postal = "08430"
            country_code = "ES"
            city = a.city or "<MISSING>"
            info = d.xpath("./following-sibling::div[1]/div/text()")
            phone = "<MISSING>"
            for i in info:
                if "Teléfono" in i:
                    phone = str(i).replace("Teléfono:", "").strip()
            hours_of_operation = (
                " ".join(d.xpath("./following-sibling::div[1]/div/text()"))
                .replace("\n", "")
                .split(f"{phone}")[1]
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
