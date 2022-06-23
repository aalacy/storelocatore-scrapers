import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.regissalons.co.uk/"
    api_url = "https://www.regissalons.co.uk/salon-locator?show-all=yes"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="list-salons"]/ul/li/ul/li//a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
        except:
            time.sleep(5)
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
        info_ad = tree.xpath('//p[@class="address"]//text()')
        info_ad = list(filter(None, [b.strip() for b in info_ad]))
        ad = (
            " ".join(tree.xpath('//p[@class="address"]//text()'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            " ".join(ad.split())
            .replace("Regis Hair Salon", "")
            .replace("Regis Hair & Beauty", "")
            .replace("Beauty by Regis", "")
            .replace("Mops Hair Salon", "")
            .replace("Regis", "")
            .strip()
        )
        location_name = "".join(
            tree.xpath('//p[@class="phone"]/preceding-sibling::*[1]//text()')
        ).strip()

        street_address = "".join(info_ad[1]).strip()
        state = "<MISSING>"
        postal = "".join(info_ad[-1]).strip()
        country_code = "UK"
        city = "".join(info_ad[-2]).strip()
        latitude = "".join(tree.xpath("//div/@data-lat"))
        longitude = "".join(tree.xpath("//div/@data-lng"))
        phone = (
            "".join(tree.xpath('//p[@class="phone"]//text()')).replace("\n", "").strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h5[text()="Opening Hours"]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
