from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://thebuffalospot.com/our-spots/",
    "cookie": "_ga=GA1.1.91499491.1615464213; _fbp=fb.1.1615464213085.817309877; apbct_antiflood_passed=35be2acbf0d7787e7e6d8ae5c25c6425; ct_checkjs=432d6ff838a22e325ab4a99027a511b8f09401e530e887d3008719807e03d9c2; apbct_site_landing_ts=1615572196; ct_sfw_pass_key=be83714398f9d23738b22f38f9f18a940; ct_ps_timestamp=1615572267; ct_timezone=-8; apbct_timestamp=1615572268; apbct_prev_referer=https%3A%2F%2Fthebuffalospot.com%2Fcalifornia%2Fvictorville%2F; apbct_page_hits=6; apbct_cookies_test=%257B%2522cookies_names%2522%253A%255B%2522apbct_timestamp%2522%252C%2522apbct_prev_referer%2522%252C%2522apbct_site_landing_ts%2522%252C%2522apbct_page_hits%2522%255D%252C%2522check_value%2522%253A%2522196fb629ca2b55da982edfd7755fee8f%2522%257D; apbct_visible_fields=%7B%7D; _ga_76X4HDK0P3=GS1.1.1615572202.3.1.1615572271.0; ct_fkp_timestamp=1615572272; ct_pointer_data=%5B%5B12%2C1043%2C4042%5D%2C%5B31%2C1041%2C4055%5D%2C%5B214%2C1037%2C4217%5D%2C%5B285%2C1034%2C4524%5D%5D",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locator_domain = "https://thebuffalospot.com"


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def _url(blocks, name):
    url = phone = ""
    for block in blocks:
        if block.h3 and block.h3.text.strip() == name:
            url = (
                locator_domain + block.find("a", href=re.compile(r"/locations"))["href"]
            )
            _phone = block.find("a", href=re.compile(r"tel:"))
            if _phone:
                phone = _phone.text
            break
    return url, phone


def fetch_data():
    with SgRequests() as session:
        base_url = "https://thebuffalospot.com/our-spots/"
        res = session.get(base_url, headers=_headers).text
        soup = bs(res, "lxml")
        blocks = soup.select("div.wpb-column.wpb-col")
        locations = json.loads(
            res.split('var map1 = $("#map1").maps(')[1]
            .strip()
            .split(').data("wpgmp_maps");')[0]
        )
        for _ in locations["places"]:
            page_url, phone = _url(blocks, _["title"])
            hours_of_operation = ""
            try:
                res1 = session.get(page_url, headers=_headers)
                if res1.status_code == 200:
                    soup1 = bs(res1.text, "lxml")
                    loc = json.loads(
                        soup1.findAll("script", type="application/ld+json")[
                            -1
                        ].string.strip()
                    )
                    hours_of_operation = _valid(loc["openingHours"])
            except:
                pass
            yield SgRecord(
                page_url=page_url,
                location_name=_["title"],
                street_address=_["address"],
                city=_["location"]["city"],
                state=_["location"]["state"],
                zip_postal=_["location"]["postal_code"],
                country_code=_["location"]["country"],
                phone=phone,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lng"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
