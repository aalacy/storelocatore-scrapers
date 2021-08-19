from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("&amp;", "&").replace("–", "-").strip()


def _phone(val):
    return val.replace("(", "").replace(")", "").replace("-", "").strip().isdigit()


def _fill_block(hours, x, blocks):
    phone = ""
    for i in range(x, len(blocks)):
        if _phone(blocks[i].text):
            phone = blocks[i].text
            break
        if not blocks[i].text.startswith("Plats"):
            hours += [
                hh
                for hh in list(blocks[i].stripped_strings)
                if hh.strip() and not hh.startswith("Horaire spécial")
            ]
    return phone


def fetch_data():
    locator_domain = "https://tuttifruttidejeuners.com/"
    base_url = "https://tuttifruttidejeuners.com/fr/restaurants/"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("var maplistScriptParamsKo = ")[1]
            .split("/* ]]> */")[0]
            .strip()[:-1]
        )
        for _ in locations["KOObject"][0]["locations"]:
            desc = bs(_["description"], "lxml")
            blocks = desc.select("p")
            addr = parse_address_intl(" ".join(blocks[0].stripped_strings))
            city = addr.city
            street_address = addr.street_address_1
            if city and len(city.split(".")) > 1:
                city = city.split(".")[-1]
                street_address += " " + city.split(".")[0]
            phone = ""
            hours = []
            location_type = ""
            for x, dd in enumerate(blocks):
                if dd.text.startswith("Fer"):
                    location_type = "Temporarily Closed"
                    for i in range(x, len(blocks)):
                        if _phone(blocks[i].text):
                            phone = blocks[i].text
                            break
                if "Lundi" in dd.text:
                    phone = _fill_block(hours, x, blocks)
                    break
                if "Tous les" in dd.text:
                    phone = _fill_block(hours, x, blocks)
                    break

            coord = (
                desc.select_one("a.viewLocationPage")["href"]
                .split("/@")[1]
                .split("z/data")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=base_url,
                location_name=bs(_["title"], "lxml").text,
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
