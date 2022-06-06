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
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def fetch_data(sgw: SgWriter):
    urls = [
        "https://www.claro.com.sv/personas/atencion-al-cliente/puntos-venta/",
        "https://www.claro.com.gt/personas/atencion-cliente/",
        "https://www.claro.com.hn/personas/atencion-al-cliente/",
        "https://www.claro.com.ni/personas/atencion-al-cliente/",
        "https://www.claro.com.pa/personas/cac/",
    ]
    for page_url in urls:
        locator_domain = page_url.split("/personas")[0]
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        divs = tree.xpath("//div[@class='listaLocalizacion']/div")
        country_code = locator_domain.split(".")[-1].upper()

        for d in divs:
            location_name = "".join(d.xpath(".//h3/text()")).strip()
            raw_address = "".join(
                d.xpath(
                    ".//dt[contains(text(), 'Distribuidor') or contains(text(), 'Dirección')]/following-sibling::dd[1]//text()"
                )
            ).strip()
            state = "".join(d.xpath("./@id"))
            street_address, city, postal = get_international(raw_address)
            try:
                text = "".join(d.xpath(".//a[contains(@href, '/@')]/@href"))
                latitude, longitude = text.split("/@")[1].split(",")[:2]
            except:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            hours_of_operation = " ".join(
                "".join(
                    d.xpath(
                        ".//dt[contains(text(), 'Horarios')]/following-sibling::dd/text()"
                    )
                ).split()
            )
            phone = SgRecord.MISSING
            if "Tel" in hours_of_operation:
                phone = hours_of_operation.split("Teléfono")[-1].strip()
                phone = phone.replace("Telefono", "").strip()
                if "/" in phone:
                    phone = phone.split("/")[-1].strip()

                hours_of_operation = hours_of_operation.split("Teléfono")[0].strip()
                if hours_of_operation.endswith("/"):
                    hours_of_operation = hours_of_operation[:-1].strip()

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
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
