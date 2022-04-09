from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("auchan.lu")


def fetch_data():
    with SgChrome().driver() as driver:
        driver.get("https://www.auchan.pl/pl/znajdz-sklep")
        result = driver.execute_async_script(
            """
            var done = arguments[0]
            fetch('https://api.woosmap.com/stores?key=woos-2f2a4a05-1e11-3393-a97a-bf416ff688ac')
                .then(res => res.json())
                .then(done)
        """
        )

        for feature in result["features"]:
            geo = feature["geometry"]
            properties = feature["properties"]

            latitude, longitude = geo["coordinates"]

            address = properties["address"]
            street_address = ",".join(address["lines"])
            city = address["city"]
            postal = address["zipcode"]
            country_code = address["country_code"]

            locator_domain = "auchan.lu"
            location_name = properties["name"]
            store_number = properties["store_id"]

            page_url = f'https://www.auchan.lu/en/retail/{properties["user_properties"]["pageName"]}'

            hours_of_operation = []
            for day, hour in properties["user_properties"]["openingHours"].items():
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

            hours_of_operation = ",".join(hours_of_operation)

            phone = properties["contact"]["phone"]

            yield SgRecord(
                locator_domain=locator_domain,
                location_name=location_name,
                page_url=page_url,
                street_address=street_address,
                city=city,
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
