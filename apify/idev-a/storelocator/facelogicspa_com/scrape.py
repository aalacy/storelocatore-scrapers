from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgpostal.sgpostal import parse_address_intl
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("facelogicspa")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.facelogicspa.com"
base_url = "http://www.facelogicspa.com/pages/spas"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.pt25.pl25.pr25.pb25 a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            if not page_url.startswith("http"):
                page_url = locator_domain + page_url
            if page_url.startswith("https"):
                page_url = page_url.replace("https", "http")
            logger.info(page_url)
            try:
                res = session.get(page_url, headers=_headers)
            except:
                continue
            if res.status_code != 200:
                continue
            sp1 = bs(res.text, "lxml")
            if not sp1.title:
                continue
            location_name = (
                sp1.title.text.split("-")[-1]
                .split("|")[-1]
                .replace("Welcome to", "")
                .strip()
                .replace("Loading...", "")
            )
            if not location_name:
                continue
            location_name = link.text.strip()
            phone = latitude = longitude = ""
            hours = []
            _addr = None
            if sp1.select_one("div.footer_custom_html"):
                tags = sp1.select_one("div.footer_custom_html").findChildren(
                    recursive=False
                )
                for x, tag in enumerate(tags):
                    if not tag.text.strip():
                        continue
                    if tag.name == "a" and tag.attrs.get("href").startswith("https"):
                        _addr = tag.text.strip()
                    if (
                        tag.name == "a"
                        and not phone
                        and tag.attrs.get("href").startswith("tel")
                    ):
                        phone = tag.text.strip()
                    if _addr and (tag.name == "i" or x == len(tags) - 1):
                        addr = parse_address_intl(_addr)
                        street_address = addr.street_address_1
                        if addr.street_address_2:
                            street_address += " " + addr.street_address_2
                        city = addr.city
                        state = addr.state
                        zip_postal = addr.postcode
                        yield SgRecord(
                            page_url=res.url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip_postal,
                            country_code="US",
                            phone=phone,
                            locator_domain=locator_domain,
                        )
                        phone = ""
                        _addr = None
            else:
                if sp1.select_one("div.sqs-block-map"):
                    ss = json.loads(
                        sp1.select_one("div.sqs-block-map")["data-block-json"]
                    )
                    location_name = ss["location"]["addressTitle"]
                    street_address = ss["location"]["addressLine1"]
                    city = ss["location"]["addressLine2"].split(",")[0]
                    state = ss["location"]["addressLine2"].split(",")[1]
                    latitude = ss["location"]["markerLat"]
                    longitude = ss["location"]["markerLng"]
                    zip_postal = sp1.h3.text.split("|")[-1].strip()
                else:
                    if sp1.select_one("div.kv-ee-footer-address"):
                        _addr = list(
                            sp1.select_one("div.kv-ee-footer-address").stripped_strings
                        )
                        if sp1.find("a", href=re.compile(r"tel:")):
                            phone = sp1.find_all("a", href=re.compile(r"tel:"))[
                                -1
                            ].text.strip()
                    elif sp1.select_one("div#footer-widget-wrap div#text-3 p"):
                        _addr = list(
                            sp1.select_one(
                                "div#footer-widget-wrap div#text-3 p"
                            ).stripped_strings
                        )[1:]
                        phone = list(
                            sp1.select("div#footer-widget-wrap div#text-3 p")[
                                1
                            ].strong.stripped_strings
                        )[0].split(":")[-1]
                    elif sp1.select_one("div.mt20.mb20 p"):
                        _addr = list(sp1.select_one("div.mt20.mb20 p").stripped_strings)
                        phone = sp1.select("div.fr")[1].text.strip()
                    elif sp1.select("div#le_footer1 div.le_content p"):
                        _addr = [
                            aa.text.strip()
                            for aa in sp1.select("div#le_footer1 div.le_content p")
                            if aa.text.strip()
                        ]
                        if "Copyright" in _addr[-1]:
                            del _addr[-1]
                        phone = _addr[-1].replace("P.", "").strip()
                        del _addr[-1]
                    elif sp1.select("div.footer-widgets-1 section#text-26 p"):
                        _addr = list(
                            sp1.select("div.footer-widgets-1 section#text-26 p")[
                                1
                            ].stripped_strings
                        )
                        if "Terms of" in _addr[-1]:
                            del _addr[-1]
                        if "|" in _addr[-1]:
                            del _addr[-1]
                        if "Privacy Policy" in _addr[-1]:
                            del _addr[-1]
                        if "Tel" in _addr[-1]:
                            phone = _addr[-1].split(":")[-1].replace("Tel", "").strip()
                            del _addr[-1]
                        hours = list(
                            sp1.find("h3", string=re.compile(r"^Our Hours"))
                            .find_next_sibling()
                            .stripped_strings
                        )[1:]
                    elif sp1.select_one("span.sub-title"):
                        _addr = list(sp1.select_one("span.sub-title").stripped_strings)
                        hours = list(
                            sp1.select_one("div.section-desc").stripped_strings
                        )
                        if "Call" in hours[0]:
                            phone = hours[0].replace("Call", "")
                            del hours[0]
                    elif sp1.select_one("div#footerinfo p"):
                        _addr = sp1.select_one("div#footerinfo p").text.split("|")
                        phone = _addr[-1]
                        del _addr[-1]
                    if not _addr:
                        continue
                    addr = parse_address_intl(" ".join(_addr))
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    city = addr.city
                    state = addr.state
                    zip_postal = addr.postcode
                yield SgRecord(
                    page_url=res.url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code="US",
                    phone=phone.strip(),
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
