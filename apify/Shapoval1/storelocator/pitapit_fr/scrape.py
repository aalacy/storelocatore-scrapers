from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pitapit.fr/"
    api_url = "https://pitapit.fr/restaurants/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="liste"]/div')
    for d in div:

        page_url = "".join(d.xpath('.//a[@class="gotoresto"]/@href'))
        cms = "".join(d.xpath('.//b[contains(text(), "Ouverture prochaine")]/text()'))
        if cms:
            continue
        location_name = "".join(d.xpath('.//p[@class="lieu"]/text()'))
        ad = (
            "".join(d.xpath('.//p[@class="adresse"]/text()'))
            .replace("\r\n", " ")
            .replace("44 000", "44000")
            .replace("35 000", "35000")
            .replace(",", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "FR"
        city = a.city or "<MISSING>"
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lon"))
        phone = "".join(d.xpath('.//p[@class="tel"]/text()')) or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            "".join(tree.xpath('//p[@class="horaires"]/text()'))
            .replace("\n", "")
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
