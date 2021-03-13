from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import json

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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


def _h(val):
    if val:
        return val
    else:
        return "closed"


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.homfurniture.com"
        base_url = "https://www.homfurniture.com/info/our-stores/locations"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        with SgChrome() as driver:
            script = soup.select_one("script", type="text/inject-data").string
            locations = json.loads(
                driver.execute_script('return decodeURIComponent("' + script + '")')
            )
            for _ in locations["fast-render-data"]["collectionData"]["Location"][0]:
                if not _.get("locations"):
                    continue
                page_url = (
                    "https://www.homfurniture.com/location/"
                    + _["locations"][0]["locationURL"]
                )
                hours_of_operation = ""
                if _["locationHours"][0]:
                    hours_of_operation = "Su: " + _h(_["locationHours"][0]["sunday"])
                    hours_of_operation += "; Mo" + _h(_["locationHours"][0]["monday"])
                    hours_of_operation += "; Tu" + _h(_["locationHours"][0]["tuesday"])
                    hours_of_operation += "; We" + _h(
                        _["locationHours"][0]["wednesday"]
                    )
                    hours_of_operation += "; Th" + _h(_["locationHours"][0]["thursday"])
                    hours_of_operation += "; Fr" + _h(_["locationHours"][0]["friday"])
                    hours_of_operation += "; Sa" + _h(_["locationHours"][0]["saturday"])
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["title"],
                    street_address=_["locations"][0]["address"],
                    city=_["locations"][0]["city"],
                    state=_["locations"][0]["state"],
                    zip_postal=_["locations"][0]["zip"],
                    country_code="US",
                    phone=_["locations"][0]["phoneNumber"],
                    latitude=_["locations"][0]["lattitude"],
                    longitude=_["locations"][0]["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation=_valid(hours_of_operation),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
