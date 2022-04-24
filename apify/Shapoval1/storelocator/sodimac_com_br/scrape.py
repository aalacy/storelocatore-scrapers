from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sodimac.com.br/"
    api_url = "https://www.sodimac.com.br/sodimac-br/content/a490001/Lojas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h4/following-sibling::ul/li/a")
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.sodimac.com.br{slug}"
        if (
            page_url
            == "https://www.sodimac.com.br/sodimac-br/content/a200004/Pagina-Inicial"
        ):
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath("//h2//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        ad = (
            "".join(
                tree.xpath(
                    '//*[contains(text(), "Localização")]/following-sibling::*[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        postal = str(postal).replace("CEP", "").replace("PRÓXIMO", "").strip()
        country_code = "BR"
        city = a.city or "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//*[contains(text(), "Telefone")]/following-sibling::*[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "(011) 3004 5678"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath('//table[.//td[contains(text(), "Loja")]]//tbody//text()')
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Tiradentes") != -1:
            hours_of_operation = (
                "Domingo " + hours_of_operation.split("Domingo")[1].strip()
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
