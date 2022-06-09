from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tuttabella.com/"
    api_url = "https://www.tuttabella.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//header[@class="site-header"]/div[@class="site-header-desktop"]//nav//button[contains(text(), "Locations")]/following-sibling::div//ul/li/a'
    )
    for d in div:

        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.tuttabella.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h1/text()"))
        street_address = (
            "".join(
                tree.xpath(
                    '//div[@class="col-md-6"]//a[contains(@href, "maps")]/text()[1]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="col-md-6"]//a[contains(@href, "maps")]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        latitude = "".join(tree.xpath("//div/@data-gmaps-lat"))
        longitude = "".join(tree.xpath("//div/@data-gmaps-lng"))
        phone = (
            "".join(
                tree.xpath('//div[@class="col-md-6"]//a[contains(@href, "tel")]/text()')
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="col-md-6"]//p[./a[contains(@href, "tel")]]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        cls = "".join(tree.xpath('//p[contains(text(), "temporarily closure")]/text()'))
        if cls:
            hours_of_operation = "Temporarily Closed"

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
