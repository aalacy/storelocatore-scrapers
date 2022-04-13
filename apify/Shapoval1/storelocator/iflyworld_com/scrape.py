from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.iflyworld.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.iflyworld.com",
        "Connection": "keep-alive",
        "Referer": "https://www.iflyworld.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    params = {
        "controller": "tunnel",
        "method": "get_tunnels",
    }

    data = {
        "controller": "tunnel",
        "method": "get_tunnels",
        "uri": "https://api2-cache.iflyworld.com/api.php?controller=tunnel&method=get_tunnels",
        "language": "en-US",
        "token": "",
    }

    r = session.post(
        "https://api2-cache.iflyworld.com/api.php",
        headers=headers,
        params=params,
        data=data,
    )
    js = r.json()
    for j in js:

        location_name = j.get("name")
        street_address = j.get("address") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        if country_code != "US":
            continue
        slug = j.get("slug")
        page_url = f"https://www.iflyworld.com{slug}"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        with SgFirefox() as driver:

            driver.get(page_url)
            a = driver.page_source
            tree = html.fromstring(a)

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//table[@class="location-hours"]//tr//td//text() | //h6[text()="HOURS"]/following-sibling::p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split()).replace("TBD", "").strip()
                or "<MISSING>"
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
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {city}, {state} {postal}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
