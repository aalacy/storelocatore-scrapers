import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://magnitcosmetic.ru/"
    api_url = "https://magnitcosmetic.ru/local/ajax/city_popup.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@class="i-select__select js-select_region"]/option')
    for d in div:
        state_id = "".join(d.xpath(".//@value"))
        state = "".join(d.xpath(".//text()"))
        r = session.get(
            f"https://magnitcosmetic.ru/local/ajax/get_city.php?region_id={state_id}",
            headers=headers,
        )
        js = r.json() or []
        for j in js:
            city_id = j.get("id")
            city = j.get("text")
            cookies = {
                "geo_city_id": f"{city_id}",
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Connection": "keep-alive",
                "Referer": "https://magnitcosmetic.ru/shops/",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
            }

            r = session.get(
                "https://magnitcosmetic.ru/shops/map/", headers=headers, cookies=cookies
            )
            tree = html.fromstring(r.text)
            jsblock = (
                "".join(tree.xpath('//script[contains(text(), "shopDataList")]/text()'))
                .split("var shopDataList = ")[1]
                .strip()
            )
            js = json.loads(jsblock)
            for j in js["shops"]:
                store_number = j.get("id")
                page_url = f"https://magnitcosmetic.ru/shops/{store_number}/"
                street_address = j.get("name") or "<MISSING>"
                country_code = "RU"
                latitude = j.get("coords").get("lat") or "<MISSING>"
                longitude = j.get("coords").get("lng") or "<MISSING>"
                hours_of_operation = j.get("time") or "<MISSING>"

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=SgRecord.MISSING,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=SgRecord.MISSING,
                    country_code=country_code,
                    store_number=store_number,
                    phone=SgRecord.MISSING,
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
