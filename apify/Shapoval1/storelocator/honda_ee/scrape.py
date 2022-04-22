from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.ee/"
    page_url = "https://cars.honda.ee/dealer-search"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="page"]//h3')
    for d in div:

        location_name = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        ad = "".join(d.xpath(".//following::p[1]/text()[1]")).replace("\n", "").strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if street_address == "Tallinna":
            street_address = ad.split(",")[0].strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "EE"
        city = "".join(d.xpath(".//preceding::h2[1]/text()")).split(".")[1].strip()
        info = d.xpath(".//following::p[1]/text() | .//following::p[2]/text()")
        info = list(filter(None, [a.strip() for a in info]))
        phone = "<MISSING>"
        for i in info:
            if "Info" in i:
                phone = "".join(i)
                break
        phone = (
            phone.replace("Info:", "").replace("Info ja tööde vastuvõtt:", "").strip()
        )
        hours_of_operation = "<MISSING>"
        for i in info:
            if "Automüük" in i or "E - R 8.00 - 17.00, L – P suletud" in i:
                hours_of_operation = "".join(i)
                break
        hours_of_operation = (
            hours_of_operation.replace("Automüük:", "")
            .replace("Automüük ja teenindus:", "")
            .replace("\n", "")
            .strip()
        )

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
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
