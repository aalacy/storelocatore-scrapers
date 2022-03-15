from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.boloco.com"
    page_url = "https://www.boloco.com/locations/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h4]")

    for d in div:

        location_name = (
            "".join(d.xpath(".//p[1]//text() | .//p[1]/span//text()"))
            .replace("\n", "")
            .strip()
        )
        street_address = "".join(d.xpath('.//span[@class="address"]/text()'))
        if street_address.find("OPEN") != -1:
            street_address = street_address.split("DELIVERY")[1].strip()
        city = "".join(d.xpath('.//span[@class="town"]/text()')).split(",")[0]
        state = (
            "".join(d.xpath('.//span[@class="town"]/text()')).split(",")[1].split()[0]
        )
        country_code = "US"
        postal = (
            "".join(d.xpath('.//span[@class="town"]/text()')).split(",")[1].split()[1]
        )
        page_url = (
            "".join(d.xpath('.//a[contains(text(), "DETAILS")]/@href'))
            or "https://www.boloco.com/locations/"
        )
        if page_url == "http://www.boloco.com/atlantic-wharf/":
            page_url = "https://www.boloco.com/locations/"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = (
            "".join(d.xpath('.//span[@class="links"]//span[@class="phone"]/text()'))
            .replace("\n", "")
            .replace("-----", "")
            .strip()
        ) or "<MISSING>"
        if phone == "<MISSING>":
            phone = (
                "".join(d.xpath('.//span[@class="phone"]/text()'))
                .replace("\n", "")
                .replace("-----", "")
                .strip()
            ) or "<MISSING>"
        if phone.find("Closed") != -1:
            phone = phone.split("Closed")[0]
        hours_of_operation = (
            "".join(d.xpath('.//p[.//strong[contains(text(), "Sun")]]//text()'))
            .replace(": -", " Closed")
            .strip()
        )

        hours_of_operation = " ".join(hours_of_operation.split())
        tmp = "".join(d.xpath('.//strong[text()="CLOSED TEMPORARILY"]/text()'))
        if tmp:
            hours_of_operation = "Temporarily Closed"
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        if page_url != "https://www.boloco.com/locations/":
            session = SgRequests()
            r = session.get(page_url)
            tree = html.fromstring(r.text)
            map_link = "".join(tree.xpath("//iframe/@src"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"

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
