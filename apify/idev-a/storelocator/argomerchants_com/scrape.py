from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("agromerchants")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://agromerchants.com"
base_url = "https://agromerchants.com/network/"

streets = []


def fetch_data():
    with SgRequests() as session:
        links = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var wpgmaps_localize_marker_data =")[1]
            .split("var wpgmaps_localize_cat_ids")[0]
            .strip()[:-1]
        )["2"]
        logger.info(f"{len(links)} found")
        for key, link in links.items():
            page_url = link["linkd"]
            if not page_url.startswith("http"):
                page_url = locator_domain + link["linkd"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _addr = parse_address_intl(
                sp1.select_one('h1[data-elementor-setting-key="title"]')
                .find_next_sibling()
                .text.strip()
            )
            country_code = _addr.country
            aa = list(
                sp1.find("h4", string=re.compile(r"Details"))
                .find_parent()
                .stripped_strings
            )[1:]
            addr = parse_address_intl("  ".join(aa).replace("‘", "'"))
            city = addr.city
            zip_postal = ""
            if country_code == "The Netherlands":
                aa_0 = aa[0]
                if aa_0.endswith(","):
                    aa_0 = aa[0][:-1]
                city = _addr.city.replace("‘", "'")
                zip_postal = (
                    aa[1]
                    .split(city)[0]
                    .replace(",", "")
                    .replace("Netherlands", "")
                    .replace(country_code, "")
                    .replace("Maasvlakte", "")
                    .strip()
                )
                if len(aa_0.split(",")) > 1 and not zip_postal:
                    zip_postal = aa_0.split(",")[1].strip()
                street_address = aa_0.replace(zip_postal, "").replace(",", "").strip()
                if "2691 MG" in street_address:
                    street_address = street_address.replace("2691 MG", "")
                    zip_postal = "2691 MG"
            else:
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                zip_postal = addr.postcode
            if country_code == "Portugal" and not zip_postal:
                street_address = aa[0].replace(",", "")
                zip_postal = aa[1].split(city)[0].replace(",", "")
            if street_address in streets:
                continue
            streets.append(street_address)
            phone = ""
            pp = sp1.find_all("a", href=re.compile(r"tel:"))
            if len(pp) > 2:
                phone = pp[0].text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=key,
                location_name=link["title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                latitude=link["lat"],
                longitude=link["lng"],
                raw_address="  ".join(aa),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
