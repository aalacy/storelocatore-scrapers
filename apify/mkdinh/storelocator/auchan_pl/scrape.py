import re
from time import sleep
from bs4 import BeautifulSoup
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("auchan.pl")


def get_location_type(types):
    for type in types:
        if type == "129":
            return "Supermarket"
        elif type == "132":
            return "Moje Auchan"

        return type


def get_locations(session):
    session.get("https://www.auchan.pl/pl/znajdz-sklep")
    session.execute_async_script("open('https://www.auchan.pl/pl/znajdz-sklep')")
    sleep(10)
    session.refresh()
    sleep(10)
    soup = BeautifulSoup(session.page_source, "html.parser")
    logger.info(session.page_source)

    return [
        f"https://www.auchan.pl{item['href']}"
        for item in soup.find_all("a", class_="store-card")
    ]


def get_store_number(name, session):
    result = session.execute_async_script(
        f"""
        var done = arguments[0]
        fetch('https://api.auchan.com/corp/cms/v4/pl/template/store-pages/{name}?lang=pl', {{
            headers: {{
                'X-Gravitee-Api-Key':'f3fef77a-534a-4223-8907-47382f646efa'
            }}
        }})
            .then(res => res.json())
            .then(done)
        """
    )

    return result["storeID"]


def get_location(store_number, session):
    result = session.execute_async_script(
        f"""
        var done = arguments[0]
        fetch('https://api.auchan.com/corp/cms/v4/pl/template/stores/{store_number}?lang=pl', {{
            headers: {{
                'X-Gravitee-Api-Key':'f3fef77a-534a-4223-8907-47382f646efa'
            }}
        }})
            .then(res => res.json())
            .then(done)
        """
    )

    return result


def get_types(session):
    result = session.execute_async_script(
        """
        var done = arguments[0]
        fetch('https://api.auchan.com/corp/cms/v4/pl/template/store-types?lang=pl', {
            headers: {
                'X-Gravitee-Api-Key':'f3fef77a-534a-4223-8907-47382f646efa'
            }
        })
            .then(res => res.json())
            .then(done)
        """
    )

    return result


def fetch_data():

    with SgChrome(is_headless=True).driver() as driver:
        types = get_types(driver)

        for page_url in get_locations(driver):
            slug = re.split("/", page_url)[-1]
            store_number = get_store_number(slug, driver)
            data = get_location(store_number, driver)

            address = data["address"]
            city = address["city"]
            state = address["region"]
            postal = address["postalCode"]
            country_code = address["country"]
            street_address = re.split(r"\s*,\s*", address["address"])[0]
            latitude = address["latitude"]
            longitude = address["longitude"]

            locator_domain = "auchan.pl"
            for type in types:
                if type["slug"] == data["type"]:
                    location_type = type["name"]
                    break

            location_name = data["pageName"]
            store_number = data["id"]

            hours_of_operation = []
            for day, hour in data["openingHours"].items():
                is_open = hour["isOpen"]
                is_open_all_day = hour.get("isOpenAllDay", False)
                if not is_open:
                    hours_of_operation.append(f"{day}: Closed")
                elif is_open_all_day:
                    hours_of_operation.append(f"{day}: Open all day")
                else:
                    start = hour["hours"][0]["start"]
                    end = hour["hours"][0]["end"]
                    hours_of_operation.append(f"{day}: {start}-{end}")

            hours_of_operation = ", ".join(hours_of_operation)

            phone = data["contact"]["phone"]

            yield SgRecord(
                locator_domain=locator_domain,
                location_name=location_name,
                location_type=location_type,
                page_url=page_url,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    data = fetch_data()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)
