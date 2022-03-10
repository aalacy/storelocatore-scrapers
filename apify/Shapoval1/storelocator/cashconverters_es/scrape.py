from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cashconverters.es/"
    api_url = "https://cashconverters.es/tiendas/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div/h3/following-sibling::ul/li//a")
    for d in div:

        slug = "".join(d.xpath(".//@href"))

        page_url = f"https://cashconverters.es{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = "".join(
            tree.xpath(
                '//h3[./strong/a[text()="Dirección de Cash Converters"]]/following-sibling::p/text()'
            )
        )
        location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
        street_address = ad.split("-")[0].strip() or "<MISSING>"
        if street_address == "<MISSING>":
            continue
        postal = ad.split("-")[-2].strip()
        country_code = "ES"
        city = ad.split("-")[-1].strip()
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "shopLatitud")]/text()'))
            .split("var shopLatitud = ")[1]
            .split("\n")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "shopLatitud")]/text()'))
            .split("var shopLongitud = ")[1]
            .split("\n")[0]
            .strip()
        )
        phone = (
            "".join(tree.xpath('//p[contains(text(), "Tel:")]/text()[1]'))
            .replace("\n", "")
            .replace("Tel:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//h3[./strong[text()="Días apertura"]]/following-sibling::p/text()'
                )
            )
            + " ".join(
                tree.xpath(
                    '//h3[./strong[text()="Horario de apertura"]]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()).strip() or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
