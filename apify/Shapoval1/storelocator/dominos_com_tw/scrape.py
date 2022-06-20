from lxml import html
from sgscrape.sgrecord import SgRecord
from datetime import datetime
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dominos.com.tw/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
        "Connection": "keep-alive",
        "Referer": "https://www.dominos.com.tw/Home/Carryout?mode=&backUrl=",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    r = session.get(
        "https://www.dominos.com.tw/Ajax/GetStoreMapMakers", headers=headers
    )
    js = r.json()
    for j in js:
        store_number = j.get("id")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("type")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-Requested-With": "XMLHttpRequest",
            "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
            "Connection": "keep-alive",
            "Referer": "https://www.dominos.com.tw/Home/Carryout?mode=&backUrl=",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        params = {
            "storeId": f"{store_number}",
        }

        r = session.get(
            "https://www.dominos.com.tw/Stores/GetStoreDialog",
            params=params,
            headers=headers,
        )
        tree = html.fromstring(r.text)

        page_url = "https://www.dominos.com.tw/Home/Carryout?mode=&backUrl="
        location_name = "".join(tree.xpath('//p[@class="stroe-name"]/text()'))
        ad = (
            "".join(
                tree.xpath(
                    '//div[./img[contains(@src, "icon_location")]]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "TW"
        city = a.city or "<MISSING>"
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]//text()')) or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="store-time-info"]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("星期六", "Saturday")
            .replace("星期日", "Sunday")
            .replace("星期一", "Monday")
            .replace("星期二", "Tuesday")
            .replace("星期三", "Wednesday")
            .replace("星期四", "Thursday")
            .replace("星期五", "Friday")
            or "<MISSING>"
        )
        today = datetime.today().strftime("%A")
        hours_of_operation = (
            str(today) + " " + " ".join(hours_of_operation.split()[1:]).strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
