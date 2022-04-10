from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    regions = ["N", "M", "S", "E"]

    for region in regions:
        data = {"Info.StoreArea": region}
        r = session.post(page_url, headers=headers, data=data)
        tree = html.fromstring(r.text)
        divs = tree.xpath("//table[@class='table bable-stores']/tbody/tr")

        for d in divs:
            location_name = "".join(d.xpath("./td[1]/text()")).strip()
            raw_address = "".join(d.xpath("./td[2]/text()")).strip()

            line = d.xpath("./td[3]/text()")
            line = list(filter(None, [li.strip() for li in line]))
            phone = line.pop(0)
            hours_of_operation = line.pop()

            street_address, city, state, postal = get_international(raw_address)
            country_code = "TW"

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.0800076666.com.tw/"
    page_url = "http://www.0800076666.com.tw/Stores/StoresLocation"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "http://www.0800076666.com.tw",
        "Connection": "keep-alive",
        "Referer": "http://www.0800076666.com.tw/Stores/StoresLocation",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
