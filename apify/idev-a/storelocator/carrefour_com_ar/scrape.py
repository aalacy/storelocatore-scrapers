from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import stop_after_attempt, retry
import time
from sglogging import SgLogSetup
import ssl
import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-ca:{}@proxy.apify.com:8000/"


ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("")

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://carrefour.com.ar/"
ar_base_url = "https://www.carrefour.com.ar/_v/public/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=es-AR&operationName=getStoreLocations&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22a84a4ca92ba8036fe76fd9e12c2809129881268d3a53a753212b6387a4297537%22%2C%22sender%22%3A%22lyracons.lyr-store-locator%400.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22eyJhY2NvdW50IjoiY2FycmVmb3VyYXIifQ%3D%3D%22%7D"
br_base_url = "https://www.carrefour.com.br/localizador-de-lojas"
br_json_url = r"https://www.carrefour.com.br/_v/public/graphql/v1\?workspace=master\&maxAge=short\&appsEtag=remove\&domain=store"

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


@retry(stop=stop_after_attempt(2))
def stop_after_2_attempts(session, hh):
    locations = []
    try:
        locations = session.get(br_base_url, headers=hh).json()["data"]["documents"]
    except:
        hh = {}
        raise Exception

    return locations


def _d(loc):
    location_type = (
        street_address
    ) = (
        city
    ) = zip_postal = phone = location_name = latitude = longitude = store_number = ""
    for _ in loc["fields"]:
        if _["key"] == "logradouro":
            street_address = _["value"]
        if _["key"] == "cidade":
            city = _["value"]
        if _["key"] == "lat":
            latitude = _["value"]
        if _["key"] == "lng":
            longitude = _["value"]
        if _["key"] == "cep":
            zip_postal = _["value"]
        if _["key"] == "loja":
            location_name = _["value"]
        if _["key"] == "primaryPhone":
            phone = _["value"]
        if _["key"] == "id":
            store_number = _["value"]
        if _["key"] == "tipo":
            location_type = _["value"]

    return SgRecord(
        page_url=br_base_url,
        store_number=store_number,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=zip_postal,
        latitude=latitude,
        longitude=longitude,
        country_code="BR",
        phone=phone,
        location_type=location_type,
        locator_domain=locator_domain,
    )


def fetch_data():
    with SgRequests() as session:
        locations = session.get(ar_base_url, headers=headers).json()["data"][
            "documents"
        ]

        for loc in locations:
            street_address = (
                city
            ) = (
                state
            ) = (
                zip_postal
            ) = phone = location_name = latitude = longitude = store_number = ""
            temp = {}
            for _ in loc["fields"]:
                if _["key"] == "addressLineOne":
                    street_address = _["value"]
                if _["key"] == "addressLineTwo" and _["value"] != "null":
                    street_address += " " + _["value"]
                if _["key"] == "locality":
                    city = _["value"]
                if _["key"] == "latitude":
                    latitude = _["value"]
                if _["key"] == "longitude":
                    longitude = _["value"]
                if _["key"] == "postalCode":
                    zip_postal = _["value"]
                if _["key"] == "labels":
                    location_name = _["value"]
                if _["key"] == "administrativeArea":
                    state = _["value"]
                if _["key"] == "primaryPhone":
                    phone = _["value"] if _["value"] != "null" else ""
                if _["key"] == "storeCode":
                    store_number = _["value"]
                if _["key"].replace("Hours", "") in days:
                    temp[f"{_['key'].replace('Hours', '')}"] = _["value"]

            if zip_postal == "null":
                zip_postal = ""

            hours = []
            for day in days:
                if temp.get(day):
                    hours.append(f"{day}: {temp[day]}")

            yield SgRecord(
                page_url="https://www.carrefour.com.ar/sucursales",
                store_number=store_number,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=latitude,
                longitude=longitude,
                country_code="AR",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


def get_url(url):
    with SgRequests() as session:
        session.get(url, headers=headers)


def fetch_br():
    with SgChrome(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        is_headless=True,
    ) as driver:
        driver.get(br_base_url)
        checks = []
        checks.append(driver.find_element_by_css_selector("input#simple-check2"))
        checks.append(driver.find_element_by_css_selector("input#simple-check3"))
        checks.append(driver.find_element_by_css_selector("input#simple-check4"))
        checks.append(driver.find_element_by_css_selector("input#simple-check5"))
        checks.append(driver.find_element_by_css_selector("input#simple-check6"))
        for check in checks:
            del driver.requests
            driver.execute_script("arguments[0].click();", check)
            time.sleep(10)
            driver.wait_for_request(br_json_url)

        x = 0
        while True:
            try:
                rr = driver.wait_for_request(br_json_url)
                locations = get_url(rr.url).json()["data"]["documents"]
                logger.info(f"page {x}, {len(locations)}")
                for loc in locations:
                    yield _d(loc)

                del driver.requests

                button = driver.find_elements_by_css_selector(
                    "div.carrefourbr-carrefour-components-0-x-showMoreButton button"
                )
                if button:
                    del driver.requests
                    x += 1
                    try:
                        banner = driver.find_element_by_css_selector(
                            "button.onetrust-close-btn-handler.banner-close-button"
                        )
                        if banner:
                            banner.click()
                            time.sleep(1)
                    except:
                        pass
                    button[0].click()
                    time.sleep(5)
                else:
                    break
            except:
                pass


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

        results_br = fetch_br()
        for rec in results_br:
            writer.write_row(rec)
