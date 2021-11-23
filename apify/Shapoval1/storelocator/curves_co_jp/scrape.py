from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.curves.co.jp"
    api_url = "https://www.curves.co.jp/search/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//map[@name="ImageMap"]/area')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        spage_url = f"https://www.curves.co.jp{slug}"
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="cityttl"]')
        for d in div:
            state = "".join(d.xpath('.//preceding::div[@class="prefttl"][1]/text()'))
            city = "".join(d.xpath(".//text()"))
            st_city = f"{state}{city}"
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Connection": "keep-alive",
                "Referer": "https://www.curves.co.jp/search/",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
            }

            api_url = f"https://www.curves.co.jp/search/lp/searchShopInCity.php?s={st_city}&ouchi=0"
            r = session.get(api_url, headers=headers)
            tree = html.fromstring(r.text)
            block = tree.xpath('//div[@class="shopdata"]')
            for b in block:

                location_name = "".join(b.xpath('.//a[@class="name-link"]/text()'))
                slug = "".join(b.xpath('.//a[@class="name-link"]/@href'))
                if not slug:
                    continue
                page_url = f"https://www.curves.co.jp{slug}"
                hours_of_operation = (
                    " ".join(b.xpath(".//table/tr[1]//td/text()"))
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
                street_address = "".join(b.xpath('.//p[@class="shopadd"]/text()'))
                country_code = "JP"
                phone = (
                    " ".join(b.xpath(".//table/tr[2]//td/text()"))
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
                    zip_postal=SgRecord.MISSING,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
