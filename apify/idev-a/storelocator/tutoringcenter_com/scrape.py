from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("tutoringcenter")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://tutoringcenter.com"
base_url = "https://tutoringcenter.com/centers/"


def _d(http, link, country="US"):
    if "comingsoon" in link["class"]:
        return
    location_name = link.h3.text.strip()
    if "UAE" in location_name:
        country = "UAE"
    url = link.select_one("a.button")["href"]
    addr = []
    for aa in link.select("p"):
        if not aa.text.strip():
            continue
        if "Director" in aa.text:
            break
        addr += list(aa.stripped_strings)
    logger.info(f"[{country}] {url}")
    hours = []
    coord = ["", ""]
    street_address = city = state = zip_postal = phone = ""
    res = http.get(url, headers=_headers)
    if res.status_code == 200:
        url = res.url
        sp1 = bs(res.text, "lxml")
        try:
            coord = (
                sp1.find("a", string=re.compile(r"^GET DIRECTIONS"))["href"]
                .split("/@")[1]
                .split("/data")[0]
                .split(",")
            )
        except:
            coord = ["", ""]
        _hr = sp1.find("span", string=re.compile(r"^HOURS", re.I))
        if not _hr:
            _hr = sp1.find("div", string=re.compile(r"^HOURS", re.I))
        if not _hr:
            _hr = sp1.find("span", string=re.compile(r"^Academic HOURS", re.I))
        if _hr:
            hours = []
            for hh in _hr.find_parent().find_parent().stripped_strings:
                if (
                    "summer" in hh.lower()
                    or "love" in hh.lower()
                    or "through" in hh.lower()
                    or "sat/act" in hh.lower()
                ):
                    break
                if "Programs" in hh or "hour" in hh.lower() or "now" in hh.lower():
                    continue
                hours.append(hh)
        if country == "US":
            if sp1.select_one("span.number"):
                phone = sp1.select_one("span.number").text.strip()
            else:
                h3 = sp1.select_one(
                    "div.breezi-app div.app-body.app-content.content-type h3"
                )
                if len(h3.findChildren(recursive=False)) > 1:
                    phone = h3.findChildren(recursive=False)[0].text.strip()
                    if phone.lower() == "phone:":
                        phone = h3.text.strip()
                else:
                    phone = list(h3.stripped_strings)[-1]
        else:
            phone = sp1.select(
                "div.breezi-app div.app-body.app-content.content-type p"
            )[3].text.strip()

        if phone:
            phone = phone.split(":")[-1].strip()

    if country == "US":
        street_address = " ".join(addr[:-1])
        city = " ".join(addr[-1].split(" ")[:-2])
        state = addr[-1].split()[-2]
        zip_postal = addr[-1].split()[-1].strip()
    else:
        street_address = addr[0].split("-")[0].strip()
        city = addr[0].split("-")[1].strip()

    return SgRecord(
        page_url=url,
        location_name=location_name,
        street_address=street_address,
        city=city.replace(",", ""),
        state=state.replace(",", ""),
        zip_postal=zip_postal,
        country_code=country,
        latitude=coord[0],
        longitude=coord[1],
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
        raw_address=" ".join(addr),
    )


def fetch_data(http: SgRequests):
    links = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "div.location-entry"
    )
    for link in links:
        yield _d(http, link)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            results = fetch_data(http)
            for rec in results:
                if rec:
                    writer.write_row(rec)
