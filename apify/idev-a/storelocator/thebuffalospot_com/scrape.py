from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://thebuffalospot.com/our-spots/",
    "cookie": "_ga=GA1.1.91499491.1615464213; _fbp=fb.1.1615464213085.817309877; apbct_antiflood_passed=35be2acbf0d7787e7e6d8ae5c25c6425; ct_checkjs=432d6ff838a22e325ab4a99027a511b8f09401e530e887d3008719807e03d9c2; apbct_site_landing_ts=1615572196; ct_sfw_pass_key=be83714398f9d23738b22f38f9f18a940; ct_ps_timestamp=1615572267; ct_timezone=-8; apbct_timestamp=1615572268; apbct_prev_referer=https%3A%2F%2Fthebuffalospot.com%2Fcalifornia%2Fvictorville%2F; apbct_page_hits=6; apbct_cookies_test=%257B%2522cookies_names%2522%253A%255B%2522apbct_timestamp%2522%252C%2522apbct_prev_referer%2522%252C%2522apbct_site_landing_ts%2522%252C%2522apbct_page_hits%2522%255D%252C%2522check_value%2522%253A%2522196fb629ca2b55da982edfd7755fee8f%2522%257D; apbct_visible_fields=%7B%7D; _ga_76X4HDK0P3=GS1.1.1615572202.3.1.1615572271.0; ct_fkp_timestamp=1615572272; ct_pointer_data=%5B%5B12%2C1043%2C4042%5D%2C%5B31%2C1041%2C4055%5D%2C%5B214%2C1037%2C4217%5D%2C%5B285%2C1034%2C4524%5D%5D",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locator_domain = "https://thebuffalospot.com"


def fetch_data():
    with SgRequests() as session:
        base_url = "https://www.thebuffalospot.com/locations/"
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("locations:")[1]
            .split("apiKey:")[0]
            .strip()[:-1]
        )
        for _ in locations:
            page_url = locator_domain + _["url"]
            if "Coming Soon" in _["hours"]:
                continue
            hours = []
            temp = list(bs(_["hours"], "lxml").stripped_strings)
            if temp:
                temp = temp[:-1]
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone_number"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("–", "-")
                .replace("&ndash;", "-")
                .replace("’til", "-"),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
