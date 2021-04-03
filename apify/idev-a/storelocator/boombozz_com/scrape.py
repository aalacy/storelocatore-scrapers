from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def _addr(block, x):
    address = " ".join(block[:x])
    addr = parse_address_intl(address.split("|")[0].strip())
    phone = ""
    if _phone(address.split("|")[-1]):
        phone = address.split("|")[-1].strip()
    return addr, phone


def fetch_data():
    locator_domain = "https://caliburger.com"
    base_url = "https://boombozz.com/locations/"
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div#allLocations > div.x-container"
        )
        for _ in locations:
            if not _.select("div.x-text p"):
                continue
            block = list(_.select_one("div.x-text").stripped_strings)
            location_type = ""
            if block[0].startswith("We will be reopening"):
                location_type = "Closed"
                del block[0]

            addr = None
            phone = ""
            for x, bb in enumerate(block):
                if "Dine In" in bb:
                    addr, phone = _addr(block, x)
                    break
                if bb.replace("–", "-").split("-")[0].strip() in days:
                    addr, phone = _addr(block, x)
                    break

            hours = []
            for hh in block[x:]:
                if "Delivery" in hh:
                    break
                if "Dine In" in hh:
                    continue
                text = (
                    hh.replace("–", "-")
                    .replace("&", "-")
                    .replace("|", ":")
                    .replace("\xa0", " ")
                )
                if text.split("-")[0].strip() in days:
                    hours.append(text)
                elif hours:
                    last = hours.pop()
                    hours.append(last + text)
            try:
                coord = (
                    _.select("li")[-1]
                    .a["href"]
                    .split("/@")[1]
                    .split("z/data")[0]
                    .split(",")
                )
            except:
                try:
                    _.select("li")[-1].a["href"].split("ll=")[1].split("&z")[0].split(
                        ","
                    )
                except:
                    pass
            yield SgRecord(
                page_url=_.select("li")[-2].a["href"],
                location_name=_.h2.text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=phone,
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
