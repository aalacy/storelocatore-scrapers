from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.localfoodstexas.com"
    api_url = "https://www.localfoodstexas.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="SubMenu-1"]/ul/li/a')

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        page_url = f"https://www.localfoodstexas.com{page_url}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//title//text()")).split("|")[0].strip()
        street_address = (
            "".join(
                tree.xpath(
                    '//section[@id="intro"]//p[./a[contains(@href, "maps")]]/a[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        ) or "<MISSING>"
        ad = (
            "".join(
                tree.xpath(
                    '//section[@id="intro"]//p[./a[contains(@href, "maps")]]/a[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )

        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"

        state = ad.split()[1].strip()
        postal = ad.split()[2].strip()
        city = ad.split()[0]
        country_code = "US"

        ll = "".join(tree.xpath('//div[@class="gmaps"]/@data-gmaps-static-url-mobile'))
        latitude, longitude = "<MISSING>", "<MISSING>"
        if ll:
            latitude = ll.split("center=")[1].split("%2C")[0]
            longitude = ll.split("center=")[1].split("%2C")[1].split("&")[0]
        hours_of_operation = "".join(
            tree.xpath(
                '//section[@id="intro"]//p[./a[contains(@href, "maps")]]/following-sibling::p[1]//text()'
            )
        )
        location_type = "Local Foods"
        cms = "".join(tree.xpath('//span[contains(text(), "COMING SOON!")]/text()'))
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=street_address + " " + ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
