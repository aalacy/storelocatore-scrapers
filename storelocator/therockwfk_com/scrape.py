from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from bs4.element import NavigableString
from sgscrape.sgpostal import parse_address_intl
import re
import json

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xc3\\xa9", "e")
            .replace("\\xa0\\xa", " ")
            .replace("\\xa0", " ")
            .replace("\\xae", " ")
        )
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.therockwfp.com/"
        base_url = "https://www.therockwfp.com/locations-all/"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.fusion-layout-column div.fusion-text a")
        for link in links:
            soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            name_block = soup1.select_one("h2.google-cityname")
            location_name = _valid1([_ for _ in name_block.stripped_strings][0])
            addr = parse_address_intl(
                " ".join(
                    [_ for _ in name_block.next_sibling.next_sibling.stripped_strings]
                )
            )
            hour_block = soup1.find("p", string=re.compile("DAILY HOURS"))
            hours = []
            for block in hour_block.next_siblings:
                if type(block) == NavigableString:
                    continue
                if not block.text or block.text.startswith("ORDER"):
                    break
                hours.append(":".join([_ for _ in block.stripped_strings]))
            maps = json.loads(soup1.select_one("div.wpgmza_map")["data-settings"])

            yield SgRecord(
                store_number=maps["id"],
                page_url=link["href"],
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=soup1.find("a", href=re.compile("tel:")).text,
                latitude=maps["map_start_lat"],
                longitude=maps["map_start_lng"],
                locator_domain=locator_domain,
                hours_of_operation=_valid1("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
