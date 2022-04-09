from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dunkin.com.br/"
    api_url = "https://dunkin.com.br/lojas-fisicas/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="elementor-accordion-item"]')
    for d in div:

        page_url = "https://dunkin.com.br/lojas-fisicas/"
        location_name = "".join(d.xpath("./div[1]//a/text()"))
        ad = "".join(d.xpath("./div[2]/p[1]/text()")).strip()
        a = parse_address(International_Parser(), ad)
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "BR"
        city = a.city or "<MISSING>"
        if city.find("/") != -1:
            city = city.split("/")[0].strip()
        if "Brasília" in ad:
            city = "Brasília"
        if "Goiânia" in ad:
            city = "Goiânia"
        street_address = (
            ad.split(f"{city}")[0]
            .replace("-", "")
            .replace("–", "")
            .replace(",", "")
            .strip()
        )
        if "Asa Norte" in ad:
            city = "Brasília"
            street_address = ad.split(",")[0].strip()

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
