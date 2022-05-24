from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    page_url = "https://www.prezunic.com.br/lojas/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='item']")

    for d in divs:
        street_address = (
            "".join(d.xpath(".//p[contains(text(), 'Endereço:')]/text()"))
            .replace("Endereço:", "")
            .strip()
        )
        city = (
            "".join(d.xpath(".//p[contains(text(), 'Cidade:')]/text()"))
            .split("–")[0]
            .replace("Cidade:", "")
            .strip()
        )
        state = (
            "".join(d.xpath(".//p[contains(text(), 'Estado:')]/text()"))
            .split("–")[-1]
            .replace("Estado:", "")
            .strip()
        )
        postal = (
            "".join(d.xpath(".//p[contains(text(), 'CEP:')]/text()"))
            .replace("CEP:", "")
            .strip()
        )
        country_code = "BR"
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        phone = (
            "".join(d.xpath(".//p[contains(text(), 'Telefone:')]/text()"))
            .replace("Telefone:", "")
            .strip()
        )
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        text = "".join(d.xpath(".//iframe/@src"))
        latitude, longitude = get_coords_from_embed(text)

        hours = d.xpath(".//p[contains(text(), 'Horário')]/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours[1:])

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.prezunic.com.br/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests(verify_ssl=False)
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
