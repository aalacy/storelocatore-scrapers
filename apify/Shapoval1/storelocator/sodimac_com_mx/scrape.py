from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sodimac.com.mx/"
    api_url = "https://www.sodimac.com.mx/sodimac-mx/content/a40055/Tiendas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@id="folder_5"]//li//a')
    for d in div:
        slug = "".join(d.xpath("./@href"))
        page_url = f"https://www.sodimac.com.mx{slug}"
        if page_url.find("Corporativo") != -1:
            continue

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = (
            "".join(
                tree.xpath(
                    '//span[text()="Venta Telefónica"]/following-sibling::span//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//strong[text()="Nuestras Tiendas"]/following-sibling::div[1]/span[2]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        iframe = "".join(tree.xpath('//iframe[contains(@src, "maps")]/@src'))
        r = session.get(iframe)
        tree = html.fromstring(r.text)
        js_block = (
            "".join(tree.xpath('//script[contains(text(), "initEmbed")]/text()'))
            .split("initEmbed(")[1]
            .split(");")[0]
            .replace("null", "None")
            .strip()
        )
        js = eval(js_block)
        try:
            ad = js[21][3][0][1]
        except:
            ad = "<MISSING>"
        location_name = ad.split(",")[0].strip()
        adr = (
            "".join(ad)
            .replace(f"{location_name},", "")
            .replace(", N.L.", "")
            .replace(", Mor.", "")
            .replace(", Méx.", "")
            .replace(", S.L.P.", "")
            .replace(", Ver.", "")
            .replace(", Gto.", "")
            .strip()
        )
        street_address = "<MISSING>"
        postal = "<MISSING>"
        country_code = "MX"
        city = page_url.split("Tienda-")[1].replace("-", " ").strip()
        if adr != "<MISSING>":
            postal = adr.split(",")[-1].split()[0].strip()
            street_address = adr.split(f", {postal}")[0].strip()
        try:
            latitude = js[21][3][0][2][0]
            longitude = js[21][3][0][2][1]
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
