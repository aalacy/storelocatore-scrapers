from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "http://grkfresh.com/"
base_url = "http://grkfresh.com/locations/"


def _coord(stores, name):
    coord = ["", ""]
    addr = None
    for store in stores:
        if name.lower() == store["title"].lower():
            coord = [store["lat"], store["lng"]]
            addr = parse_address_intl(store["address"])
            break
    return coord, addr


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        scripts = soup.select("div.map script")
        stores = []
        for script in scripts:
            dd = json.loads(
                script.string.split("JSON.parse('")[1]
                .split("gmwdmapData[")[0]
                .strip()[:-3]
            )
            stores += dd.values()
        locations = []
        for ll in soup.select("div.location")[:-1]:
            locations += ll.select(".row > div")
        for _ in locations:
            location_name = _.h4.text
            if "Dubai" in location_name:
                continue
            address = list(_.select("p")[0].stripped_strings)
            hours = []
            for pp in _.select("p")[::-1]:
                if not pp.text.strip():
                    continue
                for hh in list(pp.stripped_strings):
                    if "Delivery" in hh:
                        continue
                    if "Order Now" in hh:
                        continue
                    if "Pickup" in hh:
                        continue
                    hours.append(hh)
                break
            if "Permanently Closed" in " ".join(hours):
                continue
            coord, addr = _coord(stores, location_name)
            city = addr.city
            if city == "Washington":
                city = "Washington D.C."
            state = addr.state
            if state == "D.C. Dc":
                state = "DC"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=address[0].replace(",", " ").strip(),
                city=city,
                state=state,
                zip_postal=addr.postcode,
                phone=_p(_.select("p")[1].text.strip()),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(address),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
