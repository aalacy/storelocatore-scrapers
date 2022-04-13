from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = SgRecord.MISSING
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "http://mosburger-hk.com/shop.html"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@id='shop_list']/h4")
    for d in divs:
        location_name = "".join(d.xpath("./img/@alt"))
        store_number = "".join(d.xpath("./a/@id")).replace("shop", "")
        table = d.xpath("./following-sibling::table[1]")[0]
        raw_address = " ".join(" ".join(table.xpath(".//tr[1]/td/text()")).split())
        phone = "".join(table.xpath(".//tr[2]/td/text()")).strip()
        hours_of_operation = " ".join(
            " ".join(table.xpath(".//tr[3]/td/text()")).split()
        )
        if "西環一田店" in location_name:
            hours_of_operation = (
                table.xpath(".//tr[3]/td/text()")[0].split("：")[-1].strip()
            )
        street_address, city, state, postal = get_international(raw_address)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="HK",
            store_number=store_number,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://mosburger-hk.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
