from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.falabella.com.co/"
    page_url = "https://www.falabella.com.co/falabella-co/page/servicio-al-cliente?staticPageId=13000002#nuestras-tiendas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div[@class="store-hours"]]')
    for d in div:

        location_name = "".join(
            d.xpath('.//preceding::h3[@class="store-title"][1]//text()')
        )
        info = d.xpath('.//preceding-sibling::div[@class="store-address"][1]/p/text()')
        info = list(filter(None, [a.strip() for a in info]))
        ad = "".join(info[0]).replace("\n", "").strip()
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CO"
        phone = "<MISSING>"
        if len(info) > 1:
            phone = "".join(info[-1]).strip()
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="store-hours"]//p/text()'))
            .replace("\n", " ")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("NIT") != -1:
            hours_of_operation = "<MISSING>"
        slug = "".join(
            d.xpath(
                './/preceding::div[contains(@id, "tienda")][1]/following::div[contains(@id, "tienda")][1]/@id'
            )
        )
        city = (
            "".join(d.xpath(f'.//preceding::div[./a[@href="#{slug}"]]/@class'))
            .replace("tienda-card", "")
            .strip()
            .capitalize()
            or "<MISSING>"
        )
        if city == "<MISSING>":
            continue

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
