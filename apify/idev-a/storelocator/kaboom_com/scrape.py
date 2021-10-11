from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import demjson3 as json
import re
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("kaboom")

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "www.kaboom.com",
    "Origin": "http://www.kaboom.com",
    "Referer": "http://www.kaboom.com/findastore/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.kaboom.com/"
base_url = "http://www.kaboom.com/app/site/hosting/scriptlet.nl?script=customscript_es_findstore_sl_main&deploy=1&action=getprovinces&mode="
json_url = "http://www.kaboom.com/app/site/hosting/scriptlet.nl?script=customscript_es_findstore_sl_main&deploy=1&action=getstores&pv={}&ct=&open=undefined"


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            driver.get("http://www.kaboom.com/findastore/")
            cookies = []
            for cookie in driver.get_cookies():
                cookies.append(f"{cookie['name']}={cookie['value']}")
            _headers["cookie"] = ";".join(cookies)
            states = session.post(base_url, headers=_headers).json()["provinceObjArr"]
            for state in states:
                locations = json.decode(
                    session.get(
                        json_url.format(state["abbr"]), headers=_headers
                    ).text.split("<!")[0]
                )
                logger.info(f"[{state['abbr']}] {len(locations)}")
                for _ in locations:
                    street_address = _["address1"]
                    if _["address2"]:
                        street_address += " " + _["address2"]
                    raw_address = " ".join(
                        list(bs(_["address"], "lxml").stripped_strings)[1:]
                    )
                    page_url = locator_domain + _["urlcomponent"] + ".html"
                    logger.info(page_url)
                    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    res = (
                        sp1.find("script", string=re.compile(r"PostalAddress"))
                        .string.replace("“", '"')
                        .replace("”", '"')
                        .replace("\r\n\t", "")
                        .replace("\r\n", "")
                        .replace("\t", "")
                        .replace('"    "', '"   , "')
                    )
                    res = re.sub(r'"\s+"', '","', res)
                    res = re.sub(r">]", ">']", res)
                    res = re.sub(r"\[\s+<", "['<", res)
                    ss = json.decode(res)
                    hours = []
                    if sp1.select_one('font[face="courier new"]'):
                        hours = list(
                            sp1.select_one('font[face="courier new"]').stripped_strings
                        )
                    else:
                        hr = (
                            sp1.find("h3", string=re.compile(r"Store Hours:"))
                            .find_next_sibling("p")
                            .text.lower()
                        )
                        if "temporarily closed" in hr:
                            hours = ["temporarily closed"]
                        elif (
                            "currently closed" in hr
                            or "this location is closed" in hr
                            or "this store is closed" in hr
                        ):
                            hours = ["closed"]
                    if hours:
                        if (
                            "currently closed" in hours[0]
                            or "this location is closed" in hours[0]
                            or "this store is closed" in hours[0]
                        ):
                            hours = ["closed"]
                        if "June" in hours[0] or "July" in hours[0]:
                            hours = ["temporarily closed"]
                    yield SgRecord(
                        page_url=page_url,
                        store_number=_["store_number"],
                        location_name=_["name"],
                        street_address=street_address,
                        city=_["city"],
                        state=_["state"],
                        zip_postal=_["zip"],
                        latitude=ss["geo"]["latitude"],
                        longitude=ss["geo"]["longitude"],
                        country_code="CA",
                        phone=_["phone"],
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                        raw_address=raw_address,
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
