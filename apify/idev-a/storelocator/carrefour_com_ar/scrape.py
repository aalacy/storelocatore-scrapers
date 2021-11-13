from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl
from bs4 import BeautifulSoup as bs
import json

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = ""
ar_base_url = "https://www.carrefour.com.ar/_v/public/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=es-AR&operationName=getStoreLocations&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22a84a4ca92ba8036fe76fd9e12c2809129881268d3a53a753212b6387a4297537%22%2C%22sender%22%3A%22lyracons.lyr-store-locator%400.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22eyJhY2NvdW50IjoiY2FycmVmb3VyYXIifQ%3D%3D%22%7D"
br_base_url = "https://www.carrefour.com.br/_v/public/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=3bab9213-2811-4d32-856a-a4baa1b689b5&operationName=GET_STORES&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2218e07401147429d732eeffd9b3a526af814af3be84e09c6283f87a617f174939%22%2C%22sender%22%3A%22carrefourbr.carrefour-components%400.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22eyJhY3JvbnltIjoiTE8iLCJmaWVsZHMiOlsiYmFpcnJvIiwiY2VwIiwiY2lkYWRlIiwiY29tcGxlbWVudG8iLCJpZCIsImxhdCIsImxuZyIsImxvZ3JhZG91cm8iLCJsb2phIiwibnVtZXJvIiwidGlwbyIsInVmIl0sImFjY291bnQiOiJjYXJyZWZvdXJiciIsIndoZXJlIjoiKHVmPSdTUCcgQU5EIGNpZGFkZT0nU8OjbyBQYXVsbycpIEFORCAodGlwbz1IaXBlcikiLCJwYWdlU2l6ZSI6MjAsInBhZ2UiOjF9%22%7D"
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def fetch_data():
    with SgRequests() as session:
        with SgChrome() as driver:
            locations = session.get(ar_base_url, headers=_headers).json()["data"][
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
                        phone = _["value"]
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

            driver.get(br_base_url)
            locations = json.loads(bs(driver.page_source, "lxml").text)["data"][
                "documents"
            ]
            for loc in locations:
                location_type = (
                    street_address
                ) = (
                    city
                ) = (
                    state
                ) = (
                    zip_postal
                ) = phone = location_name = latitude = longitude = store_number = ""
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

                yield SgRecord(
                    page_url="https://www.carrefour.com.br/localizador-de-lojas",
                    store_number=store_number,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    zip_postal=zip_postal,
                    latitude=latitude,
                    longitude=longitude,
                    country_code="BR",
                    location_type=location_type,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
