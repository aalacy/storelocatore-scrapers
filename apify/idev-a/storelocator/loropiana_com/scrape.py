from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("loropiana")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://us.loropiana.com"
    base_url = "https://us.loropiana.com/en/stores"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("p.t-product-copy a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            for script in sp1.find_all("script", type="application/ld+json"):
                _ = json.loads(script.string.strip())
                hours = []
                temp = {}
                for hh in _.get("openingHoursSpecification", []):
                    days = hh["dayOfWeek"]
                    if type(hh["dayOfWeek"]) != list:
                        days = [hh["dayOfWeek"]]
                    for day in days:
                        temp[day] = temp.get(day, {})
                        if hh["opens"]:
                            temp[day]["opens"] = hh["opens"]
                        if hh["closes"]:
                            temp[day]["closes"] = hh["closes"]
                for day, hr in temp.items():
                    hours.append(f"{day}: {hr['opens']}-{hr['closes']}")

                zip_postal = _["address"]["postalCode"]
                if zip_postal.lower() == "no zip":
                    zip_postal = ""
                city = street_address = state = ""
                if (
                    _["address"]["addressCountry"].lower() == "jp"
                    or _["address"]["addressCountry"].lower() == "japan"
                ):
                    addr = parse_address_intl(
                        f'{_["address"]["streetAddress"]} {_["address"]["addressLocality"]} {zip_postal} {_["address"]["addressCountry"]}'
                    )
                    city = _["address"]["addressLocality"]
                    street_address = ", ".join(
                        _["address"]["streetAddress"].split(",")[:2]
                    )
                elif (
                    _["address"]["addressCountry"].lower() == "kr"
                    or _["address"]["addressCountry"].lower() == "korea"
                ):
                    city = _["address"]["addressLocality"]
                    street_address = _["address"]["streetAddress"]
                else:
                    addr = parse_address_intl(
                        f'{_["address"]["streetAddress"]} {_["address"]["addressLocality"]} {_["address"]["addressRegion"]} {zip_postal} {_["address"]["addressCountry"]}'
                    )
                    street_address = addr.street_address_1 or ""
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    city = addr.city
                    zip_postal = addr.postcode
                    state = addr.state
                    if not city:
                        city = _["address"]["addressLocality"]
                latitude = _["geo"]["latitude"]
                longitude = _["geo"]["longitude"]
                if latitude == "0":
                    latitude = ""
                if longitude == "0":
                    longitude = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=_["address"]["addressCountry"],
                    phone=_.get("telephone", "").split("/")[0].strip(),
                    locator_domain=locator_domain,
                    latitude=latitude,
                    longitude=longitude,
                    location_type=_["@type"],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
