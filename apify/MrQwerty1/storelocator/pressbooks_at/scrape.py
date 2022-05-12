from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table[contains(@class, 'locationsTable')]")

    for d in divs:
        location_name = "".join(
            d.xpath(".//h4/following-sibling::p[1]/strong/text()")
        ).strip()
        line = d.xpath(".//h4/following-sibling::p[1]/text()")
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = ", ".join(line).replace(" A ", " ")
        street_address = line.pop(0)
        zc = line.pop().replace("A ", "")
        postal = zc.split()[0]
        city = zc.replace(postal, "").strip()
        country_code = "AT"
        phone = (
            d.xpath(".//p[contains(text(), 'Tel')]/text()")[0]
            .replace("Tel", "")
            .replace(":", "")
            .replace(".", "")
            .strip()
        )
        hours = d.xpath(
            ".//strong[contains(text(), 'Öffnungszeiten')]/following-sibling::text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://pressbooks.at/"
    page_url = "https://pressbooks.at/index.php?id=locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
