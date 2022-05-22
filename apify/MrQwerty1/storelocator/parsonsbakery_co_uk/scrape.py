from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode

    return city, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://www.parsonsbakery.co.uk/shops"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//h2/following-sibling::p/a|//h2/following-sibling::p/strong")
    for d in divs:
        uniq = False
        header = d.xpath(".//text()")
        header = list(
            filter(
                None, [h.replace(":", "").replace("\xa0", " ").strip() for h in header]
            )
        )
        if not header:
            continue

        location_name = " ".join(header)
        text = "".join(d.xpath("./following-sibling::text()[1]"))
        text = text.replace(":", "").replace("\xa0", " ").strip()
        if "-" in text:
            street_address = text.split("-")[0].strip()
            phone = text.split("-")[-1].strip()
        elif "–" in text:
            street_address = text.replace("–", "").strip()
            phone = SgRecord.MISSING
        else:
            uniq = True
            street_address, phone = "".join(
                d.xpath("./following-sibling::text()[2]")
            ).split(" - ")

        try:
            map_url = (
                d.xpath("./@href")[0]
                .replace("%20", " ")
                .replace("%2C", ",")
                .replace("%27", "'")
            )
            if "goo.gl" in map_url:
                raise IndexError
            raw_address = map_url.split("Bakery")[1].split("&")[0].strip()
            if raw_address.endswith(","):
                raw_address = raw_address[:-1].strip()
            if raw_address.startswith(","):
                raw_address = raw_address[1:].strip()

            city, postal = get_international(raw_address)
            if city == SgRecord.MISSING:
                city = location_name
        except IndexError:
            raw_address, postal = SgRecord.MISSING, SgRecord.MISSING
            city = location_name

        if uniq:
            city = text

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.parsonsbakery.co.uk/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
