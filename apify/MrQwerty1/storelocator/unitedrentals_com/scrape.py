import json
import ssl

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(url, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)
            break
        except Exception:
            driver.quit()
            if x == 5:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def get_js(html_string):
    html_string = (
        html_string.replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .replace("</pre></body></html>", "")
    )
    return html_string


def fetch_data(sgw):
    api_url = "https://www.unitedrentals.com/api/v2/branches"

    driver = get_driver(api_url)
    response = driver.page_source
    text = get_js(response.split('pre-wrap;">')[1])
    js = json.loads(text)["data"]

    for j in js:
        page_url = f'https://www.unitedrentals.com{j.get("url")}'
        location_name = j.get("name").strip()
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("countryCode")
        store_number = j.get("branchId")
        phone = j.get("phone")
        if phone == "00":
            phone = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        start = j.get("weekdayHours").get("open")
        close = j.get("weekdayHours").get("close")
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for d in days:
            if d.startswith("sat") or d.startswith("sun") or not start:
                _tmp.append(f"{d.capitalize()}: Closed")
            else:
                _tmp.append(f"{d.capitalize()}: {start} - {close}")

        hours_of_operation = ";".join(_tmp)
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.unitedrentals.com"
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
