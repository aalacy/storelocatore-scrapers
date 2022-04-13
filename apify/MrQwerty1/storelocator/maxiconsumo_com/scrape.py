from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//li[@class='sucursal']")

    for d in divs:
        location_name = "".join(d.xpath("./span[@class='nombre']/text()")).strip()
        line = d.xpath("./address/text()")
        line = list(filter(None, [li.strip() for li in line]))
        adr = line.pop(0).split("\r\n")
        state = adr.pop().strip()
        street_address = adr.pop(0).replace(",", "").strip()
        cz = adr.pop().strip()
        city = cz.split("(")[0].strip()
        if not city:
            city = location_name
        postal = cz.split("(")[1].replace(")", "").strip()
        if postal.endswith(","):
            postal = postal[:-1]
        phone = line.pop(0)
        if "Fax" in phone:
            phone = phone.split("Fax")[0].strip()
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        hours_of_operation = ";".join(line)
        country_code = "AR"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://maxiconsumo.com/"
    page_url = "https://maxiconsumo.com/sucursales/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
