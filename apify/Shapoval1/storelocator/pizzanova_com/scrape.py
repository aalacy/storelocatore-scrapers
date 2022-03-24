from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pizzanova.com"
    api_url = "https://weborders.pizzanova.com/PNAPI/order/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//option[contains(text(), "Please")]/following-sibling::option')
    for b in block:
        city = "".join(b.xpath(".//@value"))
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://weborders.pizzanova.com",
            "Connection": "keep-alive",
            "Referer": "https://weborders.pizzanova.com/PNAPI/order/store-locator/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        data = {
            "cityName": f"{city}",
        }

        r = session.post(
            "https://weborders.pizzanova.com/PNAPI/order/getStoreListByCity",
            headers=headers,
            data=data,
        )
        js = r.json()
        for j in js:
            info = j.get("screenMsg")
            if not info:
                continue
            a = html.fromstring(info)

            page_url = "https://weborders.pizzanova.com/PNAPI/order/store-locator/"
            div = a.xpath('//div[@class="location-information"]')
            for d in div:

                ad = "".join(d.xpath(".//h2/text()"))
                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                state = a.state or "<MISSING>"
                country_code = "CA"
                city = a.city or "<MISSING>"
                hours_of_operation = (
                    " ".join(
                        d.xpath(
                            './/strong[contains(text(), "HOURS OF OPERATION")]/following-sibling::text()'
                        )
                    )
                    .replace("\n", " ")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=SgRecord.MISSING,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=SgRecord.MISSING,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=SgRecord.MISSING,
                    location_type=SgRecord.MISSING,
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
                    hours_of_operation=hours_of_operation,
                    raw_address=ad,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
