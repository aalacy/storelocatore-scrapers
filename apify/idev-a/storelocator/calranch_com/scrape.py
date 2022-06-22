from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.calranch.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-NewRelic-ID": "VgEHVV5UARABVVRXAwQAVVAC",
        "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjI3MDQ4NzkiLCJhcCI6IjExNTU0NTkyOTAiLCJpZCI6IjdkOGMyZTdmNmM3NWZiYjciLCJ0ciI6IjI0ZDQ2ZjNiNjU5YjFmZjllNGNjN2U1MDBjMDBjYjEyIiwidGkiOjE2NTU0NzI5Mzg0MTEsInRrIjoiNjUxMjU1In19",
        "traceparent": "00-24d46f3b659b1ff9e4cc7e500c00cb12-7d8c2e7f6c75fbb7-01",
        "tracestate": "651255@nr=0-1-2704879-1155459290-7d8c2e7f6c75fbb7----1655472938411",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.calranch.com",
        "Connection": "keep-alive",
        "Referer": "https://www.calranch.com/store-locator",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    params = {
        "_": "1655472938410",
    }

    r = session.post(
        "https://www.calranch.com/store_locator/location/updatemainpage",
        params=params,
        headers=headers,
    )
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[contains(@class, "mw-sl__stores__list__item")]')
    for d in div:

        page_url = "https://www.calranch.com/store-locator"
        location_name = "".join(
            d.xpath('.//span[@class="mw-sl__store__info__name"]//text()')
        )
        street_address = (
            "".join(
                d.xpath(
                    './/span[@class="mw-sl__store__info__name"]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath(
                    './/span[@class="mw-sl__store__info__name"]/following-sibling::text()[3]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].strip()
        postal = ad.split(",")[2].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "".join(d.xpath(".//div/@id"))
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html, */*; q=0.01",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-NewRelic-ID": "VgEHVV5UARABVVRXAwQAVVAC",
            "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjI3MDQ4NzkiLCJhcCI6IjExNTU0NTkyOTAiLCJpZCI6ImY1YmY2YTVjZTk4YWIzNDMiLCJ0ciI6IjBmN2NmYjMzNzFiYmY3ZTcxYjJhNTQ1M2FiODQ5YWNhIiwidGkiOjE2NTU0NzMwNTkzMDYsInRrIjoiNjUxMjU1In19",
            "traceparent": "00-0f7cfb3371bbf7e71b2a5453ab849aca-f5bf6a5ce98ab343-01",
            "tracestate": "651255@nr=0-1-2704879-1155459290-f5bf6a5ce98ab343----1655473059306",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.calranch.com",
            "Connection": "keep-alive",
            "Referer": "https://www.calranch.com/store-locator",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        params = {
            "_": "1655473059272",
            "id": f"{store_number}",
            "current_page": "cms_page_view",
        }

        data = {
            "location_ids[]": [
                "16",
                "32",
                "31",
                "30",
                "28",
                "26",
                "25",
                "24",
                "23",
                "22",
                "21",
                "20",
                "19",
                "18",
                "17",
                "1",
                "14",
                "13",
                "12",
                "11",
                "10",
                "9",
                "8",
                "7",
                "6",
                "5",
                "4",
                "3",
                "2",
            ],
        }

        r = session.post(
            "https://www.calranch.com/store_locator/location/locationdetail",
            params=params,
            headers=headers,
            data=data,
        )
        tree = html.fromstring(r.text)
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("www") != -1:
            phone = phone.split("www")[0].strip()
        hours = tree.xpath("//table//tr//text()")
        hours = list(filter(None, [a.strip() for a in hours]))
        hours_of_operation = " ".join(hours[2:])

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
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
