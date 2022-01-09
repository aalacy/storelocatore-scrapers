from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    for i in range(1, 6):
        api_url = f"https://www.shopakira.com/amlocator/index/ajax/?p={i}"

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-NewRelic-ID": "VwQGUFdQCBABVFJUDggBU1UJ",
            "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZX IiLCJhYyI6IjMyMTExMzAiLCJhcCI6IjEwMzcwMDg2NDciLCJpZCI6IjU1ZDcxNjViNjdlMTU0YzgiLCJ0ciI6ImQxZDQyZTBhZDhmNWVlNTFiMzUxNTI1MDZkZjAzYzgwIiwidGkiOjE2Mjg0OTQ5NTk5MTV9fQ==",
            "traceparent": "00-d1d42e0ad8f5ee51b35152506df03c80-55d7165b67e154c8-01",
            "tracestate": "3211130@nr=0-1-3211130-1037008647-55d7165b67e154c8----1628494959915",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.shopakira.com",
            "Connection": "keep-alive",
            "Referer": "https://www.shopakira.com/store-locator/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }
        data = {
            "lat": "0",
            "lng": "0",
            "radius": "0",
            "product": "0",
            "category": "0",
            "sortByDistance": "false",
        }

        r = session.post(api_url, headers=headers, data=data)
        js = r.json()["items"]

        for j in js:
            info = j.get("popup_html")
            a = html.fromstring(info)
            info_adr = (
                " ".join(
                    a.xpath('//div[@class="amlocator-image"]/following-sibling::text()')
                )
                .replace("\n", "")
                .strip()
            )
            street_address = (
                info_adr.split("Address:")[1]
                .split("State:")[0]
                .replace("Westfield Shopping Center", "")
                .strip()
            )
            city = info_adr.split("City:")[1].split("Zip:")[0].strip()
            state = info_adr.split("State:")[1].split("Description:")[0].strip()
            postal = info_adr.split("Zip:")[1].split("Address:")[0].strip()
            country_code = "US"
            store_number = j.get("id")
            location_name = "".join(a.xpath("//h3//text()"))

            latitude = j.get("lat")
            longitude = j.get("lng")
            page_url = "".join(a.xpath("//h3//a/@href"))

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            phone = (
                "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone == "<MISSING>":
                phone = (
                    "".join(tree.xpath('//a[contains(@href, "mailto")]/text()'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
            location_type = "<MISSING>"
            if location_name.find("COMING SOON") != -1:
                location_name = location_name.replace("***COMING SOON***", "").strip()
                location_type = "<COMING SOON>"
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@class="amlocator-schedule-table"]/div/span/text()'
                    )
                )
                .replace("\n", "")
                .strip()
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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.shopakira.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
