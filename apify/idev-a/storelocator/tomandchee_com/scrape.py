from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import re

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": "https://www.tomandchee.com/locations",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


days = ["", "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.tomandchee.com/"
        base_url = "https://locations.tomandchee.com/"
        soup = bs(session.get(base_url).text, "lxml")
        script_url = (
            base_url + soup.find_all("script", src=re.compile(r"^scripts"))[-1]["src"]
        )
        token = (
            session.get(script_url)
            .text.split('.constant("API_TOKEN",')[1]
            .split(".constant('INSTAGRAM_BUSINESS_ACCOUNT_ID'")[0]
            .strip()[1:-2]
        )
        json_url = f"https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token={token}&center=36.930407,-88.821577&coordinates=30.541266979832187,-78.51640121875123,42.82587421881942,-99.12675278125135&multi_account=false&page=1&pageSize=30"
        locations = session.get(json_url, headers=_headers).json()
        for _ in locations:
            page_url = "https://locations.tomandchee.com" + _["llp_url"]
            location_type = ""
            if _["open_or_closed"] == "coming soon":
                continue
            if _["open_or_closed"] == "closed":
                location_type = "closed"
            hours = []
            for hh in _["store_info"]["hours"].split(";"):
                if not hh:
                    continue
                time1 = hh.split(",")[1][:2] + ":" + hh.split(",")[1][2:]
                time2 = hh.split(",")[2][:2] + ":" + hh.split(",")[2][2:]
                hours.append(f"{days[int(hh.split(',')[0])]}: {time1}-{time2}")
            if not hours:
                with SgChrome() as driver:
                    driver.get(page_url)
                    soup1 = bs(driver.page_source, "lxml")
                    dt = [
                        hh.text for hh in soup1.select('dl[itemprop="openingHours"] dt')
                    ]
                    dd = [
                        hh.text for hh in soup1.select('dl[itemprop="openingHours"] dd')
                    ]
                    for key, value in dict(zip(dt, dd)).items():
                        hours.append(f"{key}: {value}")

            yield SgRecord(
                page_url=page_url,
                location_name=_["internal_ref"],
                street_address=f"{_['store_info']['address']} {_['store_info'].get('address_extended', '')} {_['store_info'].get('address3', '')}",
                city=_["store_info"]["locality"],
                state=_["store_info"]["region"],
                zip_postal=_["store_info"]["postcode"],
                country_code=_["store_info"]["country"],
                phone=_["store_info"]["phone"],
                latitude=_["store_info"]["latitude"],
                longitude=_["store_info"]["longitude"],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
