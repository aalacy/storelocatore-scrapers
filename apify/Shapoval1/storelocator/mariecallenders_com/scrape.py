from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.mariecallenders.com/wp-admin/admin-ajax.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.mariecallenders.com",
        "Connection": "keep-alive",
        "Referer": "https://www.mariecallenders.com/locations/?location=%D1%83%D0%BB.%20%D0%A1%D0%B5%D0%BD%D0%BD%D0%B0%D1%8F,%20%D0%9F%D0%BE%D0%BB%D1%82%D0%B0%D0%B2%D0%B0,%20%D0%9F%D0%BE%D0%BB%D1%82%D0%B0%D0%B2%D1%81%D1%8C%D0%BA%D0%B0%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C,%20%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0,%2036000&radius=100",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    data = {"action": "get_all_stores", "lat": "", "lng": ""}
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()
    for j in js.values():

        page_url = j.get("gu")
        location_name = j.get("na")
        location_type = "Marie Callender`s Restaurant & Bakery"
        street_address = j.get("st")
        state = j.get("rg")
        postal = j.get("zp")
        country_code = "".join(j.get("co")).strip()
        city = "".join(j.get("ct")).strip()
        store_number = j.get("ID")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("te")

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(tree.xpath('//h4[text()="Hours"]/following-sibling::p/text()'))
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
    locator_domain = "https://www.mariecallenders.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
