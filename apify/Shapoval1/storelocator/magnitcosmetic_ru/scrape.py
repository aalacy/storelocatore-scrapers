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
            r = session.get(
                f"https://magnitcosmetic.ru/shops/shop_list.php?city_id={city_id}",
                headers=headers,
            )
            tree = html.fromstring(r.text)
            div = tree.xpath('//div[@class="shops__item"]')
            for d in div:

                slug = "".join(d.xpath(".//@href"))
                page_url = f"https://magnitcosmetic.ru{slug}"
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                js_block = (
                    "".join(
                        tree.xpath(
                            '//script[contains(text(), "var oneShopData")]/text()'
                        )
                    )
                    .split("var oneShopData =")[1]
                    .strip()
                )
                js = json.loads(js_block)
                shops = js.get("shops")
                for s in shops:

                    ad = "".join(s.get("name"))
                    try:
                        street_address = (
                            ad.split(f"{city}")[1].replace(",", " ").strip()
                        )
                    except:
                        street_address = ad
                    country_code = "RU"
                    store_number = s.get("id") or "<MISSING>"
                    latitude = s.get("coords").get("lat") or "<MISSING>"
                    longitude = s.get("coords").get("lng") or "<MISSING>"
                    hours_of_operation = s.get("time") or "<MISSING>"

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
