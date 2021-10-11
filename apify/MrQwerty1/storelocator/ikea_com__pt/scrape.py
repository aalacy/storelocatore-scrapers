from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_hours(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    _tmp = []
    inters = tree.xpath(
        "//p[./strong[contains(text(), 'Store')]]/following-sibling::p/text()"
    )
    inters = list(filter(None, [inter.strip() for inter in inters]))
    days = tree.xpath(
        "//p[./strong[contains(text(), 'Store')]]/following-sibling::p/strong/text()"
    )
    for day, inter in zip(days, inters):
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.ikea.com/pt/en/stores/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    blocks = tree.xpath(
        "//div[./pub-hide-empty-link//span[contains(text(), 'store page')]]"
    )

    for b in blocks:
        d = b.xpath("./preceding-sibling::div[1]")[0]
        location_name = "".join(d.xpath(".//h3/strong/text()")).strip()
        page_url = "".join(b.xpath('.//a[@role="button"]/@href'))

        line = d.xpath(".//p[not(./a)]/text()")
        raw_address = ", ".join(list(filter(None, [l.strip() for l in line]))).replace(
            ",,", ","
        )
        street_address, city, state, postal = get_international(raw_address)

        text = "".join(d.xpath(".//p/a/@href"))
        try:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude = SgRecord.MISSING
            longitude = SgRecord.MISSING

        hours_of_operation = get_hours(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="PT",
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.ikea.com/pt"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
