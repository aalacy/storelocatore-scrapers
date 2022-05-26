from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://mxm.com.co/"
    api_url = "https://mxm.com.co/mxm/sitio/tiendas.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@id="idtienda"]/option[position() > 1]')
    for d in div:

        store_number = "".join(d.xpath(".//@value"))
        page_url = f"https://mxm.com.co/mxm/sitio/tiendas.php?idtienda={store_number}"
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//div[@class="cont_info-mapa"]//h2/text()'))
            or "<MISSING>"
        )
        ad = (
            "".join(
                tree.xpath('//td[text()="Dirección"]/following-sibling::td[1]//text()')
            )
            or "<MISSING>"
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CO"
        city = a.city or "<MISSING>"
        text = "".join(tree.xpath("//iframe/@src"))
        latitude = text.split("&center=")[1].split(",")[0].strip()
        longitude = text.split("&center=")[1].split(",")[1].split("&")[0].strip()
        phone = (
            "".join(
                tree.xpath('//td[text()="Teléfono"]/following-sibling::td[1]//text()')
            )
            or "<MISSING>"
        )
        if phone == "0":
            phone = "<MISSING>"
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//td[text()="Horario"]/following-sibling::td[1]/p[1]/text()'
                )
            )
            .replace("Parqueadero propio, al aire libre", "")
            .strip()
            or "<MISSING>"
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
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
