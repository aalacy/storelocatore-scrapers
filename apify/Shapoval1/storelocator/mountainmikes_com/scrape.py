from lxml import html
from sgscrape.sgpostal import USA_Best_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mountainmikespizza.com"
    api_url = "https://www.mountainmikespizza.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "location_block store")]')
    for d in div:

        page_url = "".join(d.xpath('.//div[@class="loc_name"]/a/@href'))
        location_name = "".join(d.xpath('.//div[@class="loc_name"]/a/text()'))
        ad = "".join(d.xpath('.//div[@class="loc_address"]/a/text()'))
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        if street_address.find("Mountain Vw") != -1:
            street_address = street_address.replace("Mountain Vw", "").strip()
            city = "Mountain Vw"
        if street_address.find("Elk Grv") != -1:
            street_address = street_address.replace("Elk Grv", "").strip()
            city = "Elk Grv"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-long"))
        phone = "".join(d.xpath('.//div[@class="loc_phone"]/a/text()')) or "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="store_hours"]/table//tr/td/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        tmp = "".join(tree.xpath('//*[contains(text(), "Temporarily Closed")]/text()'))
        if tmp:
            hours_of_operation = "Temporarily Closed"
        cms = "".join(tree.xpath('//*[contains(text(), "Coming Soon!")]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
