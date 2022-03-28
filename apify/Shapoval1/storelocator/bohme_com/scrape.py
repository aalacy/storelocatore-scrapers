import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bohme.com"
    api_url = "https://www.bohme.com/pages/store-locator"
    with SgRequests() as http:
        r = http.get(url=api_url)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="store-location-info"]')
        for d in div:

            page_url = "https://www.bohme.com/pages/store-locator"
            location_name = (
                " ".join(d.xpath(".//h3/text()")).replace("\n", "").strip()
                or "<MISSING>"
            )
            ad = (
                " ".join(d.xpath(".//h3/following-sibling::p[1]//text()"))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            a = parse_address(USA_Best_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(d.xpath('.//div[@class="info-align-bottom"]/p[last()]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
