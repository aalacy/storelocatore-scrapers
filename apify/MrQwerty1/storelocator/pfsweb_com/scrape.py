from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.pfscommerce.com/locations/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='vc_column-inner ' and .//span[@itemprop]]")
    for d in divs:
        location_name = "".join(d.xpath(".//p[./a]/span/text()")).strip()
        street_address = " ".join(
            "".join(d.xpath(".//span[@itemprop='streetAddress']/text()")).split()
        )
        city = " ".join(
            "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).split()
        )
        state = "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
        postal = "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
        country = "".join(d.xpath(".//span[@itemprop='addressCountry']/text()")).strip()

        if city[-1].isdigit():
            city, state = state, SgRecord.MISSING
        if "7" in city:
            street_address, city = city, street_address
        try:
            phone = d.xpath(".//span[@itemprop='telephone']/text()")[0].strip()
        except IndexError:
            phone = SgRecord.MISSING

        location_type = SgRecord.MISSING
        if d.xpath(".//strong[contains(text(), 'Headquarters')]"):
            location_type = "Headquarters"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            location_type=location_type,
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.pfscommerce.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
