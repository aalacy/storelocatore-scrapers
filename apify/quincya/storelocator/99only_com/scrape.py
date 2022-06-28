from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://99only.com/store-locator/%7B%22lat%22:34.895045,%22lng%22:-117.007349%7D/%7B%22lat%22:34.9592083,%22lng%22:-116.419389%7D/%7B%22south%22:23.17077877484582,%22west%22:-167.896020875,%22north%22:45.15888890484582,%22east%22:-66.118677125%7D?_format=json"
    locator_domain = "https://99only.com"

    with SgRequests() as http:
        stores = http.get(base_link, headers=headers).json()

        for store in stores:
            location_name = store["name"]
            latitude = store["lat"]
            longitude = store["lng"]
            store_number = store["num"]

            item = BeautifulSoup(store["rendered"], "lxml")
            link = locator_domain + item.find(class_="overlay-link")["href"]

            raw_address = list(item.find(class_="field").stripped_strings)
            street_address = (
                " ".join(raw_address[:-1])
                .replace("Suite 3 Suite 3 Suite 3", "Suite 3")
                .replace("Suite 108 Suite 108", "Suite 108")
            )
            if street_address == "undefined":
                street_address = location_name.split("at")[1].strip()

            city_line = raw_address[-1].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            phone = ""
            location_type = ""
            req = http.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                hours_of_operation = (
                    " ".join(
                        list(
                            base.find(class_="store-hours-list").table.stripped_strings
                        )[1:]
                    )
                    .replace("Hours", "")
                    .strip()
                )
            except:
                hours_of_operation = (
                    " ".join(list(base.find(class_="hours").stripped_strings))
                    .replace("Hours", "")
                    .strip()
                )

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
