from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import json

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://www.maxandermas.com/locations/",
    "Host": "www.maxandermas.com",
    "Cookie": "apbct_site_landing_ts=1614059484; ct_checkjs=119679886; apbct_antibot=6dcdc5436cfeea9e37a679fa8832eee8af4b91c675654f54ebc157202a31de23; _fbp=fb.1.1614059492359.1765100544; _ga=GA1.2.1580962890.1614059493; _gid=GA1.2.1933188988.1614059493; _gat=1; apbct_prev_referer=https%3A%2F%2Fwww.maxandermas.com%2F; apbct_timestamp=1614059543; apbct_page_hits=4; apbct_cookies_test=%257B%2522cookies_names%2522%253A%255B%2522apbct_timestamp%2522%252C%2522apbct_prev_referer%2522%252C%2522apbct_site_landing_ts%2522%252C%2522apbct_page_hits%2522%255D%252C%2522check_value%2522%253A%252299027d854a6dc9e6c7767308b17b2fab%2522%257D; ct_ps_timestamp=1614059543; ct_fkp_timestamp=0; ct_pointer_data=0; ct_timezone=0; apbct_visible_fields=0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def _valid(val):
    return (
        val.replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
        .replace("\\u2022", "")
    )


def _filter(blocks, hours):
    for block in blocks:
        if "SUN" in block.text:
            for _ in block.stripped_strings:
                if "DINE" in _valid(_):
                    continue
                hours += _valid(_).split("|")


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.maxandermas.com/locations/"
        base_url = "https://www.maxandermas.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMopR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABXgWuw"
        res = session.get(base_url, headers=_headers)
        locations = json.loads(res.text)["markers"]
        for location in locations:
            location_type = "<MISSING>"
            r1 = session.get(location["link"], headers=_headers)
            soup = bs(r1.text, "lxml")
            hours = []
            try:
                blocks = soup.select("div.et_pb_text_inner h2")
                _filter(blocks, hours)
                if not hours:
                    blocks = soup.select("div.et_pb_text_inner p")
                    _filter(blocks, hours)
            except:
                pass
            if (
                soup.select_one('span[color="#808080"]')
                and "TEMPORARILY CLOSED"
                in soup.select_one('span[color="#808080"]').text
            ):
                hours = ["Closed"]

            addr = parse_address_intl(location["address"])
            phone = [_ for _ in bs(location["description"], "lxml").stripped_strings][
                -1
            ]
            _phone = phone.encode("unicode-escape").decode("utf8").split("\\xa0")
            if len(_phone) > 1:
                phone = _phone[1]

            location_name = _valid(location["title"])
            if "TEMPORARILY CLOSED" in location_name:
                location_name = location_name.split("-")[0].strip()
                location_type = "Closed"
                hours = ["Closed"]

            yield SgRecord(
                page_url=location["link"],
                store_number=location["id"],
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                location_type=location_type,
                latitude=location["lat"],
                longitude=location["lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
