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
    country_code = adr.country or SgRecord.MISSING

    return street, city, state, postal, country_code


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//section[@class='microsites-cmp dzbankweb-cmp cmp-teaser-highlight']"
    )

    for d in divs:
        location_name = "".join(
            d.xpath(".//h1[@class='teaserhighlight__headline headline h3']/text()")
        ).strip()
        line = d.xpath(".//h1/following-sibling::p[1]//text()")
        line = list(filter(None, [li.strip() for li in line]))
        phone, _tmp = SgRecord.MISSING, []
        for li in line:
            if (
                "DZ" in li
                or "branch" in li.lower()
                or "office" in li.lower()
                or "postfach" in li.lower()
                or li.startswith("(")
                or "@" in li
                or "Ltd" in li
            ):
                continue
            if "telefon" in li.lower():
                phone = li.lower().replace("telefon", "").replace(":", "")
                break
            _tmp.append(li)

        raw_address = ", ".join(_tmp)
        street_address, city, state, postal, country_code = get_international(
            raw_address
        )
        if city == SgRecord.MISSING:
            city = location_name
        if state == "Central":
            state = SgRecord.MISSING
        if country_code == SgRecord.MISSING and city == "London":
            country_code = "GB"
        if country_code == SgRecord.MISSING and city == "Hong Kong":
            country_code = "HK"
        if country_code == SgRecord.MISSING:
            country_code = "DE"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.dzbank.de/"
    page_url = (
        "https://www.dzbank.de/content/dzbank/de/home/die-dz-bank/profil/standorte.html"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
