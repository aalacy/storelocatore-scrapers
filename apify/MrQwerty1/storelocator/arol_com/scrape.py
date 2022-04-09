from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode or ""
    country = adr.country or ""

    return street_address, city, state, postal, country


def fetch_data(sgw: SgWriter):
    page_url = "https://www.arol.com/en/index.php/arol-contact-us"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//td[count(p)>1]")
    for d in divs:
        location_name = "".join(d.xpath(".//p[1]//strong//text()")).strip()
        raw_address = " ".join(d.xpath(".//p")[-2].xpath(".//text()")).strip()
        street_address, city, state, postal, country = get_international(raw_address)
        if not country and "MEXICO" in raw_address:
            country = "Mexico"
        if country == "India" and "Pune" in street_address:
            city = "Pune"
            street_address = street_address.replace("Pune", "").strip()
        postal = postal.replace("C.P.", " ").replace("CEP", "").strip()

        phone = (
            "".join(
                d.xpath(
                    ".//strong[contains(text(), 'Phone')]/following-sibling::text()[1]"
                )
            )
            .replace(":", "")
            .strip()
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.arol.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
