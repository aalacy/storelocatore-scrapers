from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://koreatacobell.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://tacobell.imweb.me",
        "Connection": "keep-alive",
        "Referer": "https://tacobell.imweb.me/16",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {
        "board_code": "b20210826785825b10c2a6",
        "search": "",
        "search_mod": "all",
        "sort": "NAME",
        "status": "",
    }

    r = session.post(
        "https://tacobell.imweb.me/ajax/get_map_data.cm", headers=headers, data=data
    )
    js_block = (
        r.text.replace("\\", "").replace('"{"', '{"').replace('"}"', '"}').strip()
    )
    js = eval(js_block)
    for j in js["map_data_array"]:

        store_number = j.get("idx")
        latitude = j.get("pos_y")
        longitude = j.get("pos_x")

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://tacobell.imweb.me",
            "Connection": "keep-alive",
            "Referer": "https://tacobell.imweb.me/16",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        data = {
            "idx": f"{store_number}",
            "board_code": "b20210826785825b10c2a6",
        }

        r = session.post(
            "https://tacobell.imweb.me/ajax/get_map_post_data.cm",
            headers=headers,
            data=data,
        )
        js = r.json()
        a = js.get("post_data")
        ad = a.get("address")
        page_url = "http://koreatacobell.com/"
        location_name = a.get("subject")
        b = parse_address(International_Parser(), ad)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = b.state or "<MISSING>"
        postal = b.postcode or "<MISSING>"
        country_code = "Korea"
        city = b.city or "<MISSING>"
        phone = a.get("phone_number") or "<MISSING>"

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
