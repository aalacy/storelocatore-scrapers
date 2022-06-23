from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.royalbluegrocery.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.royalbluegrocery.com/_partials/wix-thunderbolt/dist/clientWorker.2533056c.bundle.min.js",
        "Content-Type": "application/json",
        "Authorization": "Y0qUsuowDb5WJCitWhRTm_un72VaafVavDnbZCY1cHY.eyJpbnN0YW5jZUlkIjoiNmUwYmIzNGEtYWU1ZC00YWIwLTlhMjktYjZlN2NmMTQ2ZGFjIiwiYXBwRGVmSWQiOiIxNDI3MWQ2Zi1iYTYyLWQwNDUtNTQ5Yi1hYjk3MmFlMWY3MGUiLCJtZXRhU2l0ZUlkIjoiMmU0Mzc4NmUtMTM0MS00MTJlLWE1NjYtODI0ZWNlYWRiYzQ2Iiwic2lnbkRhdGUiOiIyMDIyLTA2LTE3VDE4OjE0OjIwLjk0NFoiLCJkZW1vTW9kZSI6ZmFsc2UsImFpZCI6IjVlMDJmY2ViLTk1YzQtNDYzYS1iMjgyLTI2MjVjMzJjMjAzZSIsImJpVG9rZW4iOiI0MDQ4Y2IyNC1iZDFjLTBiOWUtM2Y0Zi0zNGE5MDFiOWQxZWEiLCJzaXRlT3duZXJJZCI6IjlhNDM5NzM3LTNmNTEtNGFhMS1iYjJhLTM5YWY0MDU5NjhmMSJ9",
        "Alt-Used": "www.royalbluegrocery.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    params = {
        "offset": "0",
        "limit": "25",
        "externalId": "b23ebc68-298b-4425-8597-b869aa68e9cf",
        "state": "PUBLISHED",
        "lang": "",
    }

    r = session.get(
        "https://www.royalbluegrocery.com/pro-gallery-webapp/v1/galleries/5992eb9f-7173-4ca6-aaca-0b7229bb9d60",
        params=params,
        headers=headers,
    )
    js = r.json()["gallery"]["items"]
    for j in js:

        page_url = j.get("link").get("url")
        location_name = j.get("title") or "<MISSING>"
        location_name = str(location_name).replace("\\xa0", " ").strip()
        phone = "".join(j.get("description")).split("\n")[1].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = "".join(tree.xpath('//p[contains(text(), "•")]/text()')) or "<MISSING>"
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        '//div[@class="_1Cu5u"]/following-sibling::div[1]//text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            ad = " ".join(ad.split()) or "<MISSING>"
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        '//div[@class="_1Cu5u"]/preceding-sibling::div[1]//text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            ad = " ".join(ad.split()) or "<MISSING>"
        if ad.find("(") != -1:
            ad = ad.split("(")[0].strip()
        ad = ad.replace("210.957.0093", "").replace("•", "").strip()
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        info = tree.xpath(
            '//div[@class="_1Q9if"]//text() | //div[@class="_2Hij5"]//text()'
        )
        info = list(filter(None, [b.strip() for b in info]))
        tmp = []
        for i in info:
            if "OPEN" in i:
                tmp.append(i)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(tree.xpath('//h6[@class="font_6"]//text()'))
                .replace("\n", "")
                .replace("609 CONGRESS AVE", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("SEE") != -1:
            hours_of_operation = hours_of_operation.split("SEE")[0].strip()
        if hours_of_operation.count("•") == 1:
            hours_of_operation = hours_of_operation.split("•")[1].strip()

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
