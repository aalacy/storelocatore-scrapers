import urllib.parse
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.haagendazs.com.mx/"
    api_url = "https://www.haagendazs.com.mx/shop/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="Directory-listLink"]')
    for d in div:
        data_count = "".join(d.xpath(".//@data-count"))
        slug = "".join(d.xpath(".//@href"))
        slug = urllib.parse.quote(slug)
        spage_url = "<MISSING>"
        page_url = "<MISSING>"
        if data_count == "(1)":
            page_url = f"https://www.haagendazs.com.mx/shop/{slug}"
        if page_url == "<MISSING>":
            spage_url = f"https://www.haagendazs.com.mx/shop/{slug}"
        if spage_url != "<MISSING>":
            session = SgRequests()
            r = session.get(spage_url, headers=headers)
            tree = html.fromstring(r.text)
            div = tree.xpath('//a[@class="Teaser-link Teaser-cta"]')
            for d in div:
                slug = "".join(d.xpath(".//@href"))
                slug = urllib.parse.quote(slug)
                page_url = f"https://www.haagendazs.com.mx/shop/{slug}"
                session = SgRequests()
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)

                location_name = (
                    " ".join(tree.xpath('//span[@itemprop="name"]/span/text()'))
                    .replace("\n", "")
                    .strip()
                )
                street_address = (
                    "".join(
                        tree.xpath(
                            '//div[@class="Core-address"]//span[@class="c-address-street-1"]/text()'
                        )
                    )
                    + " "
                    + "".join(
                        tree.xpath(
                            '//div[@class="Core-address"]//span[@class="c-address-street-2"]/text()'
                        )
                    )
                )
                state = "".join(
                    tree.xpath(
                        '//div[@class="Core-address"]//span[@class="c-address-state"]/text()'
                    )
                )
                postal = "".join(
                    tree.xpath(
                        '//div[@class="Core-address"]//span[@class="c-address-postal-code"]/text()'
                    )
                )
                country_code = "MX"
                city = "".join(
                    tree.xpath(
                        '//div[@class="Core-address"]//span[@class="c-address-city"]/text()'
                    )
                )
                latitude = "".join(
                    tree.xpath(
                        '//div[@class="Core-address"]//meta[@itemprop="latitude"]/@content'
                    )
                )
                longitude = "".join(
                    tree.xpath(
                        '//div[@class="Core-address"]//meta[@itemprop="longitude"]/@content'
                    )
                )
                phone = (
                    "".join(tree.xpath('//div[@itemprop="telephone"]/text()'))
                    or "<MISSING>"
                )
                hours_of_operation = (
                    " ".join(
                        tree.xpath('//table[@class="c-hours-details"]//tr/td//text()')
                    )
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
