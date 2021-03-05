from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.carluccios.com"


def fetch_data():
    with SgRequests() as session:
        headers = {
            "accept": "application/json, text/plain, */*",
            "cookie": "cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _gcl_au=1.1.827327943.1613421740; ajs_user_id=null; ajs_group_id=null; ajs_anonymous_id=%22100203df-a528-4d9f-9365-20f021c789e8%22; _ga=GA1.2.2016001503.1613421740; _gid=GA1.2.1949273716.1613421740; AtreemoUniqueID_cookie=3ad97329-2bb6-48c5-6da5-1c14fd9768d9-1613421742245; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWUsIm5vbi1uZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes",
            "referer": "https://www.carluccios.com/all-restaurants/",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        }
        for x in range(0, 5):
            posts_per_page = 6
            res = session.get(
                "https://www.carluccios.com/wp-admin/admin-ajax.php?id=&post_id=377&slug=all-restaurants&canonical_url=https%3A%2F%2Fwww.carluccios.com%2Fall-restaurants%2F&posts_per_page="
                + str(posts_per_page)
                + "&page="
                + str(x)
                + "&offset=&post_type=restaurant&repeater=default&seo_start_page=1&preloaded=false&preloaded_amount=0&order=ASC&orderby=title&action=alm_get_posts&query_type=standard",
                headers=headers,
                verify=False,
            )
            store_list = bs(json.loads(res.text)["html"], "lxml").select("div.column")
            for store in store_list:
                page_url = store.select_one("a")["href"]
                location_name = store.select_one("h4.is-title").text
                address_detail = store.select_one(
                    "div.all-restaurants__address"
                ).text.split("\n")
                address_detail = [x for x in address_detail if x]
                city_zip = address_detail.pop()
                zip = city_zip.split(", ").pop()
                city = ", ".join(city_zip.split(", ")[:-1])
                street_address = " ".join(address_detail)
                phone = store.select_one("div.all-restaurants__phone").text.replace(
                    "\n", ""
                )
                res = session.get(page_url, headers=headers, verify=False)
                soup = bs(res.text, "lxml")
                latitude = (
                    soup.select_one("input#restaurantLocationMap")["value"]
                    .replace("%22%3A%22", "=")
                    .replace("%22%2C%22", "&")
                    .split("&")[1]
                    .split("=")
                    .pop()
                )
                longitude = (
                    soup.select_one("input#restaurantLocationMap")["value"]
                    .replace("%22%3A%22", "=")
                    .replace("%22%2C%22", "&")
                    .split("&")[2]
                    .split("=")
                    .pop()
                )

                hours = soup.select_one(
                    "div.map-opening-times__times-inner"
                ).text.split("\n")
                hours = [x.strip() for x in hours if x]
                hours_of_operation = " ".join(hours)
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
                )
                yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
