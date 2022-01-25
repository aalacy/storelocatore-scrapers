from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data(sgw: SgWriter):
    with SgChrome(user_agent=user_agent) as driver:
        page_url = "https://www.nbtbank.com/locations/index.html"
        api = "https://www.nbtbank.com/locations/locations.json"
        driver.get(api)
        js = json.loads(driver.find_element(By.CSS_SELECTOR, "body").text)["features"]

        for j in js:
            geo = j.get("geometry", {}).get("coordinates") or [
                SgRecord.MISSING,
                SgRecord.MISSING,
            ]
            j = j.get("properties")
            location_name = j.get("name") or ""
            if "ATM" in location_name:
                continue
            street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip()
            city = j.get("city")
            state = j.get("state")
            postal = j.get("zip")
            phone = j.get("phone")
            latitude = geo[1]
            longitude = geo[0]

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            for d in days:
                if d == "Tuesday":
                    part = "Tues"
                elif d == "Thursday":
                    part = "Thurs"
                else:
                    part = d[:3]

                time = j.get(f"Lobby_{part}")
                if time:
                    _tmp.append(f"{d}: {time}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.nbtbank.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
