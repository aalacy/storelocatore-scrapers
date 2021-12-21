from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.guess.mx"

    loc_types = ["Accessories", "Factory", "Guess*Jeans"]

    for loc_type in loc_types:
        base_link = (
            "https://www.guess.mx/api/dataentities/SO/search?_where=typeStore=*"
            + loc_type
            + "*&_fields=direccion,city,horario,latitude,longitude,name,neighborhood,phone,postalCode,state,storeSellerId&_sort=name"
        )

        headers = {
            "authority": "www.guess.mx",
            "method": "GET",
            "path": "/api/dataentities/SO/search?_where=typeStore=*"
            + loc_type
            + "*&_fields=direccion,city,horario,latitude,longitude,name,neighborhood,phone,postalCode,state,storeSellerId&_sort=name",
            "scheme": "https",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "rest-range": "resources=0-49",
            "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "content-type": "application/json; charset=utf-8",
            "referer": "https://www.guess.mx/localiza-tu-tienda",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        }

        stores = session.get(base_link, headers=headers).json()

        for store in stores:
            location_name = store["name"]
            street_address = store["direccion"]
            city = store["city"]
            state = store["state"]
            zip_code = store["postalCode"]
            country_code = "Mexico"
            store_number = store["storeSellerId"]
            phone = store["phone"]
            location_type = loc_type.replace("*", " ")
            hours_of_operation = store["horario"]
            latitude = store["latitude"]
            longitude = store["longitude"]

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url="https://www.guess.mx/localiza-tu-tienda",
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
