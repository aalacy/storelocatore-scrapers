from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import demjson

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://pelicanssnoballs.com"
    base_url = "https://pelicanssnoballs.com/locations/"
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "ul.franchises li a"
        )
        for state in states:
            state_url = locator_domain + state["href"]
            cities = bs(session.get(state_url, headers=_headers).text, "lxml").select(
                "ul.franchises li a"
            )[1:]
            for city in cities:
                page_url = locator_domain + city["href"]
                res = session.get(page_url, headers=_headers).text
                soup = bs(res, "lxml")
                location_name = list(
                    soup.select_one("div.avia_textblock h1").stripped_strings
                )
                addr = list(soup.select_one("div.avia_textblock h2").stripped_strings)
                hours = [_.text for _ in soup.select("div.avia_textblock ul.hours li")]
                coord = {"lat": "", "lng": ""}
                try:
                    coord = demjson.decode(
                        res.split("var uluru =")[1]
                        .split("// The map, centered")[0]
                        .strip()[:-1]
                    )
                except:
                    pass
                phone = ""
                phone_block = list(
                    soup.select_one("div.avia_textblock p").stripped_strings
                )
                if phone_block and _phone(phone_block[0]):
                    phone = phone_block[0]

                hours_of_operation = "; ".join(hours)
                if "currently closed" in hours_of_operation:
                    hours_of_operation = "Closed"
                if "Daily Veterans" in hours_of_operation:
                    hours_of_operation = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name[0],
                    street_address=addr[0],
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                    latitude=coord["lat"],
                    longitude=coord["lng"],
                    phone=phone,
                    zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
