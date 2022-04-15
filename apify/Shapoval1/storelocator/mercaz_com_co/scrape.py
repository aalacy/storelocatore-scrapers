from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://mercaz.com.co"
    api_url = "https://mercaz.com.co/#"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@id="main-menu"]/ul//a[./span[text()="Sedes"]]/following-sibling::ul/li/a/following-sibling::ul/li/a'
    )
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h4[@class="tbk__subtitle"]/preceding::h3[1]//text()'))
            .replace("\n", " ")
            .strip()
            or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = (
                "".join(
                    tree.xpath(
                        '//h4[./span/strong[text()="Dirección:"]]/preceding-sibling::h3[1]//text()'
                    )
                )
                .replace("\n", " ")
                .strip()
                or "<MISSING>"
            )
        street_address = (
            "".join(
                tree.xpath(
                    '//b[contains(text(), "Dirección:")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", " ")
            .strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = (
                "".join(
                    tree.xpath(
                        '//span[./strong[text()="Dirección:"]]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", " ")
                .strip()
                or "<MISSING>"
            )
        if street_address == "<MISSING>":
            street_address = (
                "".join(
                    tree.xpath(
                        '//span[./strong[text()="Dirección:"]]/following-sibling::span/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        country_code = "CO"
        city = "<MISSING>"
        if "Tumaco" in location_name:
            city = "Tumaco"
        if "Medellin" in location_name:
            city = "Medellin"
        if "Cali" in location_name:
            city = "Cali"
        try:
            latitude = (
                "".join(
                    tree.xpath('//script[contains(text(), "new Zn_google_map")]/text()')
                )
                .split("new Zn_google_map")[1]
                .split("[")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(
                    tree.xpath('//script[contains(text(), "new Zn_google_map")]/text()')
                )
                .split("new Zn_google_map")[1]
                .split("[")[1]
                .split(",")[1]
                .split("]")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('//b[text()="Teléfono:"]/following-sibling::text()[1]'))
            .replace("\n", "")
            .replace("ext 9116", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    tree.xpath(
                        '//span[./strong[text()="Teléfono:"]]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    tree.xpath(
                        '//strong[text()="Teléfono:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = ""
        info = tree.xpath("//div[./h4]//text()")
        info = list(filter(None, [a.strip() for a in info]))
        tmp = []
        for i in info:
            if "pm." in i:
                tmp.append(i)
            hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
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
