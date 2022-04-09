from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.newbalance.gr/"
    api_url = "https://www.newbalance.gr/el/plirofories/katastimata/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="center-container"]/div/ul/li')
    for d in div:
        latitude = "".join(d.xpath("./div/@data-latitude")).strip() or "<MISSING>"
        longitude = "".join(d.xpath("./div/@data-longitude")).strip() or "<MISSING>"
        location_name = "".join(d.xpath('.//h2[@class="title"]/text()'))
        slug = (
            "".join(
                d.xpath(
                    './/ul[@class="info-container js-info"]/li[@class="type"]//text()'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        if slug == "NB Store":
            location_name = "New Balance Store"
        if slug == "NB Outlet":
            location_name = "New Balance Outlet"
        if slug == "NB Retailer":
            location_name = "New Balance Retailer"
        if slug == "NB Offices":
            location_name = "New Balance Offices"
        page_url = "https://www.newbalance.gr/el/plirofories/katastimata/"
        street_address = (
            "".join(d.xpath('.//span[@class="address"]//text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        state = (
            "".join(d.xpath('.//span[@class="area"]//text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        postal = (
            "".join(d.xpath('.//span[@class="postal-code"]//text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        country_code = "GR"
        city = (
            "".join(d.xpath('.//span[@class="city"]//text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()')).strip()
            or "<MISSING>"
        )
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        hours_of_operation = (
            " ".join(d.xpath('.//li[@class="description icon-open-hours"]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation.find("shop") != -1:
            hours_of_operation = "<MISSING>"

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
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
