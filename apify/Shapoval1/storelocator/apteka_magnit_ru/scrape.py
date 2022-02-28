from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://apteka.magnit.ru/"
    api_url = "https://apteka.magnit.ru/api/addresses/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["addresses"]
    for j in js:

        page_url = "<MISSING>"
        guid = j.get("guid")
        r = session.get(f"https://apteka.magnit.ru/api/addresses/{guid}/children/")
        js = r.json()["addresses"]
        for j in js:

            guid = j.get("guid")
            ids = j.get("id")
            cookies = {
                "current_address": f"%7B%22id%22%3A{ids}%2C%22name%22%3A%22%D0%B3.%20%D0%91%D0%B5%D0%BB%D0%BE%D0%B2%D0%BE%2C%20%D0%9A%D0%B5%D0%BC%D0%B5%D1%80%D0%BE%D0%B2%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%22%2C%22guid%22%3A%22{guid}%22%2C%22favorite%22%3Afalse%2C%22addressLevel%22%3A2%2C%22fullName%22%3A%22%D0%9A%D0%B5%D0%BC%D0%B5%D1%80%D0%BE%D0%B2%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%22%2C%22phone%22%3A%22%22%2C%22latitude%22%3A0%2C%22longitude%22%3A0%2C%22zoom%22%3A0%2C%22display%22%3Atrue%2C%22dateUpdate%22%3A1645386097443%7D",
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "x-browser-full-uri": "/locations?view=map",
                "x-browser-uri": "/locations",
                "Connection": "keep-alive",
                "Referer": "https://apteka.magnit.ru/locations?view=map",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }

            r = session.get(
                "https://apteka.magnit.ru/api/catalog/stores",
                headers=headers,
                cookies=cookies,
            )
            js = r.json()["stores"]
            for j in js:

                location_name = j.get("name") or "<MISSING>"
                ad = j.get("address")
                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                state = j.get("region") or "<MISSING>"
                postal = j.get("index") or "<MISSING>"
                country_code = "RU"
                city = a.city or "<MISSING>"
                store_number = j.get("id") or "<MISSING>"
                page_url = f"https://apteka.magnit.ru/locations/{store_number}"
                latitude = j.get("latitude") or "<MISSING>"
                longitude = j.get("longitude") or "<MISSING>"
                try:
                    phone = j.get("phone")[0]
                except:
                    phone = "<MISSING>"
                hours_of_operation = j.get("scheduleWork") or "<MISSING>"

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
