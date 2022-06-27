from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.der-beck.de"
    session = SgRequests()
    session.get("https://www.der-beck.de/csrftoken")

    headers = {
        "Host": "www.der-beck.de",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Length": "67",
        "Origin": "https://www.der-beck.de",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://www.der-beck.de/in-ihrer-naehe/filialfinder/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {
        "umkreis": "10000",
        "plz": "91052",
        "__csrf_token": "6RJNBGIomk0al3e06TNRGBgY6JCpjM",
    }

    r = session.post(
        "https://www.der-beck.de/in-ihrer-naehe/filialfinder/#submit",
        data=data,
        headers=headers,
    )
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="findereintrag"]')
    for d in div:

        page_url = "https://www.der-beck.de/in-ihrer-naehe/filialfinder/"
        info = d.xpath('.//div[@class="block1"]/text()')
        info = list(filter(None, [a.strip() for a in info]))
        street_address = "".join(info[0]).strip()
        ad = "".join(info[1]).replace("a.d. Pegnitz", "").strip()
        state = "<MISSING>"
        postal = ad.split()[0].strip()
        country_code = "DE"
        city = ad.split()[1].strip()
        if city.find("/") != -1:
            city = city.split("/")[0].strip()

        latitude = "".join(
            tree.xpath(f'//div[contains(@data-info, "<br>{street_address}")]/@data-lat')
        )
        longitude = "".join(
            tree.xpath(f'//div[contains(@data-info, "<br>{street_address}")]/@data-lng')
        )
        phone = "".join(info[-1]).strip()
        if street_address == "Glogauer Straße 30-38" and phone == "0911-98801585":
            latitude = "49.4027393"
            longitude = "11.1356615"
        if street_address == "Glogauer Straße 30-38" and phone == "0911/8108542":
            latitude = "49.4027393"
            longitude = "11.1356615"
        hours_of_operation = (
            " ".join(d.xpath('.//div[./strong[text()="Öffnungszeiten"]]//text()'))
            .replace("Öffnungszeiten", "")
            .replace("Bitte beachten Sie unsere", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        fetch_data(writer)
