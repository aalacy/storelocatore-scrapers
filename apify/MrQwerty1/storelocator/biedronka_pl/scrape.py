from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_ids():
    r = session.get("https://www.biedronka.pl/pl/sklepy")
    tree = html.fromstring(r.text)

    return tree.xpath("//map[@name='locationMap']/area/@data-map-id")


def fetch_data(sgw: SgWriter):
    fail_counter = 0
    for i in range(1, 5000):
        api = f"https://www.biedronka.pl/api/shop/getbycity?city={i}&special="
        r = session.get(api, headers=headers)
        try:
            js = r.json()["items"]
            if len(js) >= 1:
                fail_counter = 0
        except KeyError:
            fail_counter += 1
            js = []

        if fail_counter > 15:
            break

        for j in js:
            location_name = j.get("name")
            store_number = j.get("id")
            page_url = f"https://www.biedronka.pl/pl/shop,id,{store_number}"
            street = j.get("street") or ""
            number = j.get("street_number") or ""
            street_address = f"{street} {number}".strip()
            city = j.get("city")
            postal = j.get("zip_code")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            _tmp = []
            days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            for day in days:
                inter = j.get(f"hours_{day}")
                _tmp.append(f"{day}: {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code="PL",
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.biedronka.pl/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.biedronka.pl/pl/sklepy",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
