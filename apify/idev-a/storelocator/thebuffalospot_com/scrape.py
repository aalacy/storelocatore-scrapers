from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("thebuffalospot")

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


def fetch_data():
    with SgRequests() as session:
        base_url = "https://thebuffalospot.com/our-spots/"
        res = session.get(base_url, headers=_headers).text
        soup = bs(res, "lxml")
        blocks = soup.select("div.wpb-row-4-cols div.wpb-column.wpb-col")
        logger.info(f"{len(blocks)} found")
        for _ in blocks:
            if not _.text.strip():
                continue
            addr = parse_address_intl(" ".join(list(_.p.stripped_strings)[1:]))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_postal = addr.postcode
            latitude = longitude = ""
            phone = ""
            _phone = _.find("a", href=re.compile(r"tel"))
            if _phone:
                phone = _phone.text
            page_url = ""
            _url = _.find("a", href=re.compile(r"/locations"))
            if _url:
                page_url = locator_domain + _url["href"].replace("/locations", "")
                logger.info(page_url)
                res1 = session.get(page_url, headers=_headers)
                hours_of_operation = ""
                if res1.status_code == 200:
                    sp1 = bs(res1.text, "lxml")
                    if "COMING SOON!" in sp1.h2.text:
                        continue
                    script = json.loads(
                        sp1.select('script[type="application/ld+json"]')[-1].string
                    )
                    street_address = script["address"]["streetAddress"]
                    city = script["address"]["addressLocality"]
                    state = script["address"]["addressRegion"]
                    zip_postal = script["address"]["postalCode"]
                    latitude = script["geo"]["latitude"]
                    longitude = script["geo"]["longitude"]
                    hours_of_operation = script["openingHours"]

            yield SgRecord(
                page_url=page_url,
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation.replace("–", "-").replace(
                    "’", "'"
                ),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
