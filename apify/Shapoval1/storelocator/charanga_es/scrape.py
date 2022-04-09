from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://charanga.es/"
    api_url = "https://charanga.es/gb/module/kbstorelocatorpickup/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//ul[./li[@id]]/li")
    for d in div:

        page_url = "https://charanga.es/gb/module/kbstorelocatorpickup/stores"
        location_name = (
            "".join(d.xpath('.//div[@class="velo_add_name"]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = d.xpath('.//div[@class="velo-add-address"]/text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        adr = " ".join(ad)
        a = parse_address(International_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "ES"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = "".join(ad[-1]).strip()
            postal = "".join(ad[-2]).strip()
            street_address = "".join(ad[0]).strip()
        store_number = "".join(d.xpath("./@id"))
        latitude = "".join(d.xpath('.//input[@id="velo-add-latitude"]/@value'))
        longitude = "".join(d.xpath('.//input[@id="velo-add-longitude"]/@value'))
        phone = (
            "".join(d.xpath('.//img[contains(@src, "call")]/following-sibling::text()'))
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//table[@class="mp-openday-list"]//tr//td//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
