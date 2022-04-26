from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("simonpearce")

_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.simonpearce.com",
    "referer": "https://www.simonpearce.com/store-locator",
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.simonpearce.com"
base_url = "https://www.simonpearce.com/our-stores"
ajax_url = "https://www.simonpearce.com/amlocator/index/ajax/"


def fetch_stores():
    with SgRequests() as session:
        links = bs(session.get(base_url).text, "lxml").select("div.pagebuilder-column")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.p or not link.strong:
                continue
            page_url = link.a["href"]
            if page_url == "https://www.simonpearce.com/store-locator":
                continue
            if not page_url.startswith("https"):
                page_url = locator_domain + page_url
            logger.info(page_url)
            addr = list(link.select("p")[-1].stripped_strings)
            hours = []
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            if "COMING SOON" in res:
                continue
            _hr = sp1.find("h3", string=re.compile(r"STORE HOURS"))
            if _hr:
                _hh = _hr.find_parent().p
                if "now open" in _hh.text.lower():
                    _hh = _hr.find_parent().select("p")[1]
                hours = list(_hh.stripped_strings)
            try:
                coord = (
                    sp1.find("a", string=re.compile(r"^VIEW MAP"))["href"]
                    .split("ll=")[1]
                    .split("&")[0]
                    .split(",")
                )
            except:
                try:
                    coord = (
                        sp1.find("a", string=re.compile(r"VIEW MAP"))["href"]
                        .split("/@")[1]
                        .split("/data")[0]
                        .split(",")
                    )
                except:
                    coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=link.strong.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=" ".join(addr[1].split(",")[1].strip().split(" ")[:-1]),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="United States",
                phone=addr[-1],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


def fetch_data():
    with SgRequests() as session:
        payload = {
            "lat": "37.09024",
            "lng": "-95.712891",
            "radius": "",
            "product": "0",
            "category": "0",
            "sortByDistance": "1",
        }
        links = session.post(ajax_url, headers=_headers, json=payload).json()["items"]
        logger.info(f"{len(links)} found")
        for _ in links:
            info = bs(_["popup_html"], "lxml")
            page_url = info.a["href"].replace("&apos;", "'")
            if page_url == "https://www.simonpearce.com/store-locator":
                continue
            logger.info(page_url)
            street_address = city = state = zip_postal = country_code = phone = ""
            sp1 = bs(session.get(page_url).text, "lxml")
            blocks = sp1.select("div.amlocator-location-info div.amlocator-block")
            for bb in blocks:
                span = list(bb.stripped_strings)
                if not span:
                    continue
                if "Zip" in span[0]:
                    zip_postal = span[-1]
                elif "Country" in span[0]:
                    country_code = span[-1]
                elif "State" in span[0]:
                    state = span[-1]
                elif "City" in span[0]:
                    city = span[-1]
                elif "Address" in span[0]:
                    street_address = span[-1].replace("\n", " ").replace("\r", "")
            if not street_address and not city:
                continue
            pp = sp1.select_one("div.amlocator-location-info").find(
                "a", href=re.compile(r"tel:")
            )
            hours = ""
            if pp:
                _pp = pp.text.split()
                phone = _pp[0].strip()
                if len(_pp) > 1:
                    hours = " ".join(_pp[1:])
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=info.a.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                latitude=_["lat"],
                longitude=_["lng"],
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_stores()
        for rec in results:
            writer.write_row(rec)

        for rec in fetch_data():
            writer.write_row(rec)
