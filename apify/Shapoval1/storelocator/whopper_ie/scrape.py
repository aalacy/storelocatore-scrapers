from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.whopper.ie/"
    api_url = "https://www.whopper.ie/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="locations__list"]/div')
    for d in div:
        store_number = "".join(d.xpath(".//@data-id"))
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lng"))
        sec = (
            "".join(tree.xpath('//script[contains(text(), "security")]/text()'))
            .split('"security":"')[1]
            .split('"')[0]
            .strip()
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.whopper.ie",
            "Connection": "keep-alive",
            "Referer": "https://www.whopper.ie/locations/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }

        data = {
            "action": "load_post_by_ajax",
            "id": f"{store_number}",
            "security": f"{sec}",
        }

        r = session.post(
            "https://www.whopper.ie/wp-admin/admin-ajax.php", headers=headers, data=data
        )
        js = r.json()
        page_url = "https://www.whopper.ie/locations/"
        location_name = "".join(js.get("title")).replace("&#8217;", "’").strip()
        a = js.get("location_on_map")
        location_type = "<MISSING>"
        street_address = "".join(a.get("address"))
        state = "".join(a.get("state")) or "<MISSING>"
        postal = a.get("post_code") or "<MISSING>"
        country_code = a.get("country")
        city = a.get("city") or "<MISSING>"
        if "Dublin" in street_address:
            city = "Dublin"
        if city == "<MISSING>":
            city = state.split()[1].strip()
        if street_address.count(",") < 4:
            street_address = street_address.split(",")[0].strip()
        if street_address.count(",") > 3:
            street_address = "".join(street_address.split(",")[:2])
        phone = js.get("tel") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = js.get("openning_hours") or "<MISSING>"
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        if hours != "<MISSING>":
            for k in days:
                day = k
                opens = js.get("openning_hours").get(f"{k}").get("start")
                closes = js.get("openning_hours").get(f"{k}").get("end")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{a.get('address')}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
