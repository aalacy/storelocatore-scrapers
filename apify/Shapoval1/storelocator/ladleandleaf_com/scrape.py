from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ladleandleaf.com/"
    api_url = "https://ladleandleaf.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location"]')
    for d in div:
        slug = "".join(d.xpath(".//h1/a/@href"))
        page_url = f"https://ladleandleaf.com{slug}"
        location_name = "".join(d.xpath(".//h1/a/text()"))
        street_address = (
            "".join(d.xpath('.//div[@class="restaurant-address"]/p[1]/text()'))
            or "<MISSING>"
        )
        if location_name == "SFO - United Domestic Terminal":
            street_address = "S McDonnell Rd"
        ad = "".join(
            d.xpath(
                './/div[@class="restaurant-address"]/p[contains(text(), ",")]/text()'
            )
        )
        state = ad.split(",")[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        text = "".join(d.xpath('.//a[contains(text(), "View map")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()')).strip()
            or "<MISSING>"
        )

        hours_of_operation = (
            " ".join(d.xpath(".//p[@class='hours']//text()")).replace("\n", "").strip()
        )
        if hours_of_operation.count("Temporarily Closed") > 1:
            hours_of_operation = "Temporarily Closed"
        hours_of_operation = hours_of_operation.replace(
            "weekends July 5: Closed", ""
        ).strip()
        if (
            hours_of_operation.find("Weekdays:  Temporarily Closed Weekends:  Closed")
            != -1
        ):
            hours_of_operation = "Temporarily Closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
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
