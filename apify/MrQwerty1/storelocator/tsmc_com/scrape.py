from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or "<MISSING>"
    state = adr.state
    postal = adr.postcode
    country = adr.country

    return street_address, city, state, postal, country


def get_coords(text):
    if "@" in text:
        lat = text.split("@")[1].split(",")[0]
        lng = text.split("@")[1].split(",")[1]
        return lat, lng
    return SgRecord.MISSING, SgRecord.MISSING


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-12 col-lg-6']")

    for d in divs:
        location_name = "".join(d.xpath(".//h3[@class='contact-title']/text()")).strip()
        raw_address = "".join(
            d.xpath(".//div[@class='contact-address']/text()")
        ).strip()
        street_address, city, state, postal, country = get_international(raw_address)
        if city[0].isdigit():
            postal = city
            city = SgRecord.MISSING
        if city[-1].isdigit():
            postal = city.split()[-1]
            city = city.replace(postal, "").strip()
        phone = (
            "".join(d.xpath(".//div[@class='contact-tel']/text()"))
            .replace("TEL:", "")
            .strip()
        )
        text = "".join(d.xpath(".//div[@class='contact-others']/a/@href"))
        latitude, longitude = get_coords(text)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    locator_domain = "https://www.tsmc.com/"
    page_url = "https://www.tsmc.com/english/aboutTSMC/TSMC_Fabs"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
