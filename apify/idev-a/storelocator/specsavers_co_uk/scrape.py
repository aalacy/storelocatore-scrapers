import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.specsavers.co.uk"
        res = session.get("https://www.specsavers.co.uk/stores/full-store-list")
        soup = bs(res.text, "lxml")
        store_links = soup.select("div.item-list ul li a")
        for store_link in store_links:
            page_url = "https://www.specsavers.co.uk/stores/" + store_link["href"]
            missing_urls = [
                "https://www.specsavers.co.uk/stores/sudburysainsburys-hearing",
                "https://www.specsavers.co.uk/stores/skipton-hearing",
            ]
            if page_url in missing_urls:
                continue
            res1 = session.get(page_url)
            soup = bs(res1.text, "lxml")

            detail_url = soup.select_one("div.js-yext-info")["data-yext-url"]
            res2 = session.get(detail_url)
            store = json.loads(res2.text)
            if len(store["response"].keys()) == 0:
                location_name = soup.select_one(
                    "h1.store-header--title"
                ).string.replace("\n", "")
                address_detail = soup.select_one("div.store p").text.split("\n\n")
                zip = address_detail.pop().replace("\n", "")
                state = address_detail.pop().replace("\n", "")
                state = state[:-1] if state.endswith(",") else state
                city = address_detail.pop().replace("\n", "")
                city = city[:-1] if city.endswith(",") else city
                street_address = " ".join(address_detail).replace("\n", "").strip()
                street_address = (
                    street_address[:-1]
                    if street_address.endswith(",")
                    else street_address
                )
                geo = (
                    res1.text.split("var position = ")[1]
                    .split(";")[0]
                    .replace("{", "")
                    .replace("}", "")
                    .replace("lat:", "")
                    .replace("lng:", "")
                    .split(",")
                )
                latitude = geo[0].strip()
                longitude = geo[1].strip()
            else:
                location_name = (
                    store["response"]["locationName"]
                    if "locationName" in store["response"].keys()
                    else "<MISSING>"
                )
                street_address = (
                    store["response"]["address"]
                    if "address" in store["response"].keys()
                    else "<MISSING>"
                )
                street_address += (
                    " " + store["response"]["address2"]
                    if "address2" in store["response"].keys()
                    else ""
                )
                city = (
                    store["response"]["city"]
                    if "city" in store["response"].keys()
                    else "<MISSING>"
                )
                state = (
                    store["response"]["state"]
                    if "state" in store["response"].keys()
                    else "<MISSING>"
                )
                zip = (
                    store["response"]["zip"]
                    if "zip" in store["response"].keys()
                    else "<MISSING>"
                )
                latitude = (
                    store["response"]["yextDisplayLat"]
                    if "yextDisplayLat" in store["response"].keys()
                    else "<MISSING>"
                )
                longitude = (
                    store["response"]["yextDisplayLng"]
                    if "yextDisplayLng" in store["response"].keys()
                    else "<MISSING>"
                )
            if len(city.split(", ")) == 2:
                tmp = city.split(", ")
                state = tmp.pop()
                city = tmp[0]
            phone = soup.select_one("span.contact--store-telephone--text").string
            country_code = (
                store["response"]["countryCode"]
                if "countryCode" in store["response"].keys()
                else "<MISSING>"
            )
            store_number = (
                store["response"]["id"]
                if "id" in store["response"].keys()
                else "<MISSING>"
            )

            day_of_week = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]

            if "hours" in store["response"].keys():
                hours = store["response"]["hours"].split(",")
                hours_data = {}

                hours_of_operation = ""
                for x in hours:
                    contents = x.split(":")
                    hours_data[day_of_week[int(contents[0]) - 1]] = (
                        contents[1]
                        + ":"
                        + contents[2]
                        + "-"
                        + contents[3]
                        + ":"
                        + contents[4]
                    )
                for x in day_of_week:
                    hours_of_operation += (
                        x
                        + ": "
                        + (hours_data[x] if x in hours_data.keys() else "Closed")
                        + " "
                    )
                hours_of_operation = hours_of_operation.strip()
            else:
                hours_of_operation = "<MISSING>"
            location_type = "Hearing Centre" if "hearing" in page_url else "Optician"

            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                location_type=location_type,
                store_number=store_number,
                country_code=country_code,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
