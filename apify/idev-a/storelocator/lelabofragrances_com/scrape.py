from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import dirtyjson as json

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


locator_domain = "https://www.lelabofragrances.com"
base_url = "https://www.lelabofragrances.com/front/app/store/search?execution=e1s1"


def _country(soup, code):
    countries = soup.select("ul.all-locations-list li a")
    for country in countries:
        if country["data-country"] == code:
            return country.text.strip()


def fetch_us(res):
    locations = res.split("storeObjects.push(")[1:]
    for loc in locations:
        _ = json.loads(loc.split(");")[0].replace("js_site_var['static_path']", '""'))
        street_address = _["address1"]
        if _["address2"]:
            street_address += " " + _["address2"]
        hours = []
        if _["hours"]:
            for hh in bs(_["hours"], "lxml").stripped_strings:
                if "Available" in hh or "Order" in hh or "WhatsApp" in hh:
                    continue
                hours.append(hh)
        city = _["city"]
        zip_postal = _["zip"]
        if city == "DC":
            city = ""

        if city.isdigit() and not zip_postal:
            zip_postal = city
            city = ""

        if not city and "-" in _["name"]:
            city = (
                _["name"]
                .split("-")[0]
                .replace("LE LABO", "")
                .replace("Airport", "")
                .strip()
            )
        yield SgRecord(
            page_url=base_url,
            location_name=_["name"],
            street_address=street_address,
            city=city,
            state=_["state"],
            zip_postal=zip_postal,
            country_code="US",
            phone=_["phone"],
            latitude=_["latitude"],
            longitude=_["longitude"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours).replace("\n", "; "),
            raw_address=_["full_address"],
        )


def fetch_data():
    with SgRequests() as session:
        res = session.get(
            "https://www.lelabofragrances.ca/front/app/store/search?bypass=true&execution=e1s1&bypass=true&region=CA&locale=EN",
            headers=headers,
        ).text
        soup = bs(
            res,
            "lxml",
        )
        locations = soup.select("ul.list-location-directory > li")
        for rec_us in fetch_us(res):
            yield rec_us

        for _ in locations:
            country_code = _["class"][0].split("-")[-1]
            country = _country(soup, country_code)
            _addr = list(_.select_one("div.store-address").stripped_strings)
            raw_address = ", ".join(_addr)
            if not raw_address.endswith(country):
                raw_address += ", " + country
            if len(raw_address.split(country)) > 2:
                raw_address = raw_address.replace(country, "").strip()
                while True:
                    if raw_address.endswith(","):
                        raw_address = raw_address[:-1].strip()
                    else:
                        break
                raw_address += ", " + country

            addr = raw_address.split(",")
            street_address = city = state = zip_postal = ""
            if country_code == "UK" or country_code == "GB":
                zip_postal = addr[-2].strip()
                city = addr[-3].strip()
                street_address = " ".join(addr[:-3])
            elif country_code == "US":
                continue
            else:
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode

            if city in ["Ee", "Korea"]:
                city = ""

            if country_code == "HK":
                city = ""

            location_name = (
                _.select_one("div.store-name").text.replace("–", "-").strip()
            )
            if not city and "-" in location_name:
                city = (
                    location_name.split("-")[0]
                    .replace("LE LABO", "")
                    .replace("Airport", "")
                    .strip()
                )

            if country_code == "JP":
                street_address = _addr[0]

            if street_address in ["2 I Ga", "138 City"] or (
                street_address and street_address.replace("-", "").isdigit()
            ):
                street_address = ""
                addr = raw_address.split(",")
                idx = 0
                while True:
                    street_address += " " + addr[idx]
                    if not street_address.strip().isdigit():
                        break
                    idx += 1

            hours = []
            if _.select_one("div.store-hours"):
                for hh in _.select_one("div.store-hours").stripped_strings:
                    if "Available" in hh or "Order" in hh or "WhatsApp" in hh:
                        continue
                    hours.append(hh)
            phone = ""
            if _.select_one("div.store-number"):
                phone = _.select_one("div.store-number").text.split(":")[-1].strip()

            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\n", "; "),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
