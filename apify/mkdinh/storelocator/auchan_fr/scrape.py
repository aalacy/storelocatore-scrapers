import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("auchan.pl")


def fetch_locations(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("div", class_="place-pos")


def fetch_location(item, location_type, session):
    url = item.find("div", class_="place-pos__more").find("a").attrs["href"]
    page_url = f"https://www.auchan.fr{url}"
    response = session.get(page_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    container = soup.find("div", class_="posItem")
    store_number = re.sub(r"pos_", "", container.attrs["id"])
    location_name = soup.find("h1", class_="site-breadcrumb__title--ellipsis").text

    lat = container.attrs["data-lat"]
    lng = container.attrs["data-lng"]
    country_code = "FR"

    store_info = soup.find("div", class_="store-info")
    if store_info:
        street_address = store_info.find("meta", itemprop="streetAddress").attrs[
            "content"
        ]
        city = store_info.find("meta", itemprop="addressLocality").attrs["content"]
        postal = store_info.find("meta", itemprop="postalCode").attrs["content"]

        schedule = store_info.find("ul", class_="store-weekSchedule")
        hours_of_operation = []
        for dayhour in schedule.find_all("li"):
            day = dayhour.find("span", class_="store-weekSchedule__days").text
            hour = dayhour.find("span", class_="store-weekSchedule__hours").text

            hours_of_operation.append(f"{day}: {hour}")

        if not len(hours_of_operation):
            hours_of_operation = [
                "Lundi: Fermé",
                "Mardi: Fermé",
                "Mercredi: Fermé",
                "Jeudi: Fermé",
                "Vendredi: Fermé",
                "Samedi: Fermé",
                "Dimanche: Fermé",
            ]
        hours_of_operation = ",".join(hours_of_operation)
    else:
        address = item.find("div", class_="place-pos__address").find_all("span")
        texts = [item.text.strip() for item in address if item.text]
        if len(texts) == 1:
            street_address = None
            (postalcity,) = texts
        else:
            street_address, postalcity = texts

        postal, city = postalcity.split(" ", 1)
        hours_of_operation = None

    phone_info = soup.find("meta", itemprop="telephone")
    phone = phone_info.attrs["content"] if phone_info else None

    return SgRecord(
        page_url=page_url,
        locator_domain="auchan.fr",
        location_name=location_name,
        location_type=location_type,
        store_number=store_number,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours_of_operation,
        phone=phone,
    )


def fetch_data():
    with SgRequests() as session:
        types = ["DRIVE", "PICKUP_POINT", "LOCKERS", "HYPER", "SUPER", "PROXY"]
        session.get("https://www.auchan.fr")
        with ThreadPoolExecutor() as executor:
            for location_type in types:
                response = session.get(
                    f"https://www.auchan.fr/nos-magasins?types={location_type}"
                )
                futures = [
                    executor.submit(fetch_location, item, location_type, session)
                    for item in fetch_locations(response.text)
                ]
                for future in as_completed(futures):
                    poi = future.result()
                    if poi:
                        yield poi


if __name__ == "__main__":
    data = fetch_data()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)
