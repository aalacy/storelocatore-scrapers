import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.coppel.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6Ijc0ODkzMCIsImFwIjoiNDc0NzM4OTUzIiwiaWQiOiIwZDRlMzMwZGJmNWVlNjVhIiwidHIiOiIzYWY4NTllYzNjMzgzZjg2OGU4ZTRiMTVhY2NkMmY0MCIsInRpIjoxNjUyMjYyOTkzMzUyLCJ0ayI6IjE1NDE0NjAifX0=",
        "traceparent": "00-3af859ec3c383f868e8e4b15accd2f40-0d4e330dbf5ee65a-01",
        "tracestate": "1541460@nr=0-1-748930-474738953-0d4e330dbf5ee65a----1652262993352",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.coppel.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://www.coppel.com/ubicacion-de-tiendas-coppel",
        "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
        "Connection": "keep-alive",
    }

    params = {
        "catalogId": "10051",
        "storeId": "10151",
        "langId": "-5",
    }

    data = {
        "countryId": "10001",
        "requesttype": "ajax",
    }

    r = session.post(
        "https://www.coppel.com/AjaxProvinceSelectionDisplayView",
        params=params,
        headers=headers,
        data=data,
    )
    tree = html.fromstring(r.text)
    div = tree.xpath("//select/option")
    for d in div:
        value_state = "".join(d.xpath(".//@value"))
        state = "".join(d.xpath(".//text()"))
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6Ijc0ODkzMCIsImFwIjoiNDc0NzM4OTUzIiwiaWQiOiJiZDFhZjdmZDA3YWVhNzU0IiwidHIiOiI5MmE5MzcwOGM1Y2JjMDY1MGZiZGI5OTM2OWNkZDJhMCIsInRpIjoxNjUyMjYzMzQxOTc4LCJ0ayI6IjE1NDE0NjAifX0=",
            "traceparent": "00-92a93708c5cbc0650fbdb99369cdd2a0-bd1af7fd07aea754-01",
            "tracestate": "1541460@nr=0-1-748930-474738953-bd1af7fd07aea754----1652263341978",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.coppel.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Referer": "https://www.coppel.com/ubicacion-de-tiendas-coppel",
            "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
            "Connection": "keep-alive",
        }

        params = {
            "catalogId": "10051",
            "storeId": "10151",
            "langId": "-5",
        }

        data = {
            "provinceId": f"{value_state}",
            "requesttype": "ajax",
        }

        r = session.post(
            "https://www.coppel.com/AjaxCitySelectionDisplayView",
            params=params,
            headers=headers,
            data=data,
        )
        tree = html.fromstring(r.text)
        div = tree.xpath("//select/option")
        for d in div:
            city_value = "".join(d.xpath(".//@value"))
            city = "".join(d.xpath(".//text()"))
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "*/*",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6Ijc0ODkzMCIsImFwIjoiNDc0NzM4OTUzIiwiaWQiOiI1ZGVkN2RlMzJlOWI0YTUzIiwidHIiOiJjM2VjN2ExYjQwYWJiZmM4MjM2MWUxMmRjOTRjZmY1MCIsInRpIjoxNjUyMjYzMjczNTgwLCJ0ayI6IjE1NDE0NjAifX0=",
                "traceparent": "00-c3ec7a1b40abbfc82361e12dc94cff50-5ded7de32e9b4a53-01",
                "tracestate": "1541460@nr=0-1-748930-474738953-5ded7de32e9b4a53----1652263273580",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.coppel.com",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Referer": "https://www.coppel.com/ubicacion-de-tiendas-coppel",
                "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
                "Connection": "keep-alive",
            }

            params = {
                "catalogId": "10051",
                "orderId": "",
                "storeId": "10151",
                "langId": "-5",
            }

            data = {
                "cityId": f"{city_value}",
                "fromPage": "StoreLocator",
                "geoCodeLatitude": "",
                "geoCodeLongitude": "",
                "errorMsgKey": "",
                "requesttype": "ajax",
            }

            r = session.post(
                "https://www.coppel.com/AjaxStoreLocatorResultsView",
                params=params,
                headers=headers,
                data=data,
            )
            tree = html.fromstring(r.text)
            try:
                js_block = (
                    "".join(
                        tree.xpath('//script[contains(text(), "var store")]/text()')
                    )
                    .split("var store = JSON.parse('")[1]
                    .split("');")[0]
                    .strip()
                )
            except:
                continue
            js_block = " ".join(js_block.split())
            js = json.loads(js_block)
            for j in js:

                location_name = (
                    j.get("Description")[0].get("displayStoreName") or "<MISSING>"
                )
                ad = j.get("addressLine")[0]
                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                postal = j.get("postalCode") or "<MISSING>"
                country_code = "MX"
                store_number = j.get("storeName") or "<MISSING>"
                latitude = j.get("latitude") or "<MISSING>"
                longitude = j.get("longitude") or "<MISSING>"
                if latitude == "0.00000":
                    latitude, longitude = "<MISSING>", "<MISSING>"
                phone = j.get("telephone") or "<MISSING>"
                hours_of_operation = j.get("addressLine")[1] or "<MISSING>"
                slug_loc_name = str(location_name).replace(" ", "-").lower()
                slug = f"coppel-{slug_loc_name}-{store_number}"
                page_url = f"https://www.coppel.com/wcs/shop/coppel/{slug}"

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
