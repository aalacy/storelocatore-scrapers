from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.der-beck.de"
    session = SgRequests()
    cookies = {
        "session-1": "5b13f013cf2b7164f1398504b0bc806678adbbbec11f7a46ef834bedc6ebfd8f",
        "__csrf_token-1": "7XY8uQRV2NleK6hKmYT45abyYkZNCA",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "multipart/form-data; boundary=---------------------------286015112433308835001571930278",
        "Origin": "https://www.der-beck.de",
        "Connection": "keep-alive",
        "Referer": "https://www.der-beck.de/in-ihrer-naehe/filialfinder/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }

    data = '-----------------------------286015112433308835001571930278\r\nContent-Disposition: form-data; name="lat"\r\n\r\n\r\n-----------------------------286015112433308835001571930278\r\nContent-Disposition: form-data; name="long"\r\n\r\n\r\n-----------------------------286015112433308835001571930278\r\nContent-Disposition: form-data; name="city"\r\n\r\nErlangen\r\n-----------------------------286015112433308835001571930278\r\nContent-Disposition: form-data; name="plz"\r\n\r\n91052\r\n-----------------------------286015112433308835001571930278\r\nContent-Disposition: form-data; name="street"\r\n\r\n\r\n-----------------------------286015112433308835001571930278\r\nContent-Disposition: form-data; name="umkreis"\r\n\r\n100000\r\n-----------------------------286015112433308835001571930278\r\nContent-Disposition: form-data; name="showmap"\r\n\r\nFiliale finden\r\n-----------------------------286015112433308835001571930278\r\nContent-Disposition: form-data; name="__csrf_token"\r\n\r\n7XY8uQRV2NleK6hKmYT45abyYkZNCA\r\n-----------------------------286015112433308835001571930278--\r\n'

    r = session.post(
        "https://www.der-beck.de/in-ihrer-naehe/filialfinder/#submit",
        headers=headers,
        data=data,
        cookies=cookies,
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
