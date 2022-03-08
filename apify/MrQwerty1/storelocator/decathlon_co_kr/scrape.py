from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="box-info"]')
    for d in div:
        location_name = "".join(d.xpath(".//h3/text()"))
        ad = "".join(d.xpath(".//h3/following-sibling::p[1]/text()"))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state
        postal = a.postcode
        country_code = "KR"
        city = a.city
        phone = "".join(d.xpath('.//li[@class="phone"]/strong/text()'))
        hours_of_operation = (
            " ".join(d.xpath('.//li[@class="time"]/div//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("open :", "")
            .replace("close :", "")
            .replace("  ", " - ")
            .replace(" :", ":")
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
    locator_domain = "https://www.decathlon.co.kr/kr_en/"
    page_url = "https://www.decathlon.co.kr/kr_en/store/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
