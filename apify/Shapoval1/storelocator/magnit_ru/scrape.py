import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://magnit.ru"
    api_url = "https://magnit.ru/shops/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var  locationList")]/text()'))
        .split("var  locationList = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:
        store_number = j.get("settlementId")
        cookies = {
            "mg_geo_id": f"{store_number}",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://magnit.ru/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        }

        r = session.get("https://magnit.ru/shops/", headers=headers, cookies=cookies)
        tree = html.fromstring(r.text)
        jsblock = (
            "".join(
                tree.xpath('//script[contains(text(), "var elementsArr = ")]/text()')
            )
            .split("var elementsArr = ")[1]
            .split(";")[0]
            .strip()
        )
        try:
            js = json.loads(jsblock)["points"]
        except:
            continue
        for j in js:
            page_url = f"https://magnit.ru{j.get('href')}"
            location_type = j.get("type")
            street_address = " ".join("".join(j.get("address")).split(",")[1:]).strip()
            country_code = "RU"
            city = "".join(j.get("address")).split(",")[0].strip()
            if street_address.find(f"{city}") != -1:
                street_address = street_address.replace(f"{city}", "").strip()
            latitude = j.get("lat")
            longitude = j.get("lng")
            hours_of_operation = j.get("time")

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=SgRecord.MISSING,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=SgRecord.MISSING,
                country_code=country_code,
                store_number=store_number,
                phone=SgRecord.MISSING,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
