from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.reiss.com/"
base_url = "https://www.reiss.com/storelocator/data/stores"
country_selector = "https://www.reiss.com/countryselect"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Stores"]
        for _ in locations:
            page_url = f"https://www.reiss.com/storelocator/{_['NA'].lower().replace(' ','')}/{_['BR']}?sv=list"
            hours = []
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            info = json.loads(sp1.find("script", type="application/ld+json").string)
            addr = info["address"]
            for hh in info.get("openingHoursSpecification", []):
                hours.append(f"{hh['dayOfWeek']}: {hh['opens']} - {hh['closes']}")
            raw_address = " ".join(
                sp1.select_one("p.slm-info-address").stripped_strings
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["BR"],
                location_name=info["name"],
                street_address=addr["streetAddress"].replace("Reiss,", "").strip(),
                city=addr["addressLocality"],
                state=addr.get("addressRegion"),
                zip_postal=addr.get("postalCode"),
                latitude=_["LT"],
                longitude=_["LN"],
                country_code=addr["addressCountry"],
                phone=info["telephone"],
                location_type=info["@type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


def get_res(url):
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers)


def fetch_global():
    with SgRequests(proxy_country="us") as session:
        sp2 = bs(session.get(country_selector, headers=_headers).text, "lxml")
        countries = sp2.select("div.country-option-container")
        for country in countries:
            country_name = country.select_one("div.country-name").text.strip()
            if country_name == "United Kingdom":
                continue
            c_url = country.select_one("a.country-option")["href"]
            if c_url.startswith("//"):
                c_url = "https:" + c_url
            if not c_url.startswith("http"):
                c_url = locator_domain + c_url

            sp3 = get_res(c_url)
            locator_url = sp3.url.__str__().split("?")[0] + "/store-locator"
            logger.info(locator_url)
            sp4 = bs(get_res(locator_url).text, "lxml")
            for _ in sp4.select("ul.rs-store-list li.rs-store"):
                block = list(_.select_one("div.rs-store-details").stripped_strings)
                location_name = _.button.text.strip()
                _addr = []
                hours = []
                phone = ""
                if _.find("strong", string=re.compile(r"Tel")):
                    phone = (
                        _.find("strong", string=re.compile(r"Tel"))
                        .text.split(":")[-1]
                        .replace("Tel", "")
                        .strip()
                    )
                for x, bb in enumerate(block):
                    if "Tel" in bb:
                        _addr = block[: x - 1]
                    if "Monday" in bb:
                        _addr = block[: x - 1]
                        hours = block[x:]
                        if hours and hours[0] == "Monday:":
                            hours = []
                if not _addr:
                    _addr = block

                raw_address = ", ".join(_addr).replace("\n", " ").replace("\r", "")
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2

                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
                country_code = country_name

                if country_name == "USA":
                    if not city:
                        city = location_name.split(",")[0].strip()
                    if not state:
                        state = location_name.split(",")[-1].strip()
                if country_name == "Netherlands":
                    city = location_name
                if country_name in [
                    "Hong Kong",
                    "Argentina",
                    "Brazil",
                    "Canada",
                    "Mexico",
                ]:
                    c_n = location_name.split(",")
                    country_code = c_n[-1]
                    if len(c_n) > 1:
                        city = c_n[0]
                if not city:
                    if country_name in ["Germany"]:
                        city = location_name.split(",")[-1].strip()
                    if country_name in ["Ireland"]:
                        city = location_name.split("-")[0].strip()
                yield SgRecord(
                    page_url=locator_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

        g_results = fetch_global()
        for rec in g_results:
            writer.write_row(rec)
