from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_header1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def _phone(val):
    if (
        val.replace("-", "")
        .replace(" ", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
        .isdigit()
    ):
        return val
    return ""


def fetch_data():
    names = []
    with SgRequests() as session:
        locator_domain = "https://cinnaholic.com"
        base_url = "https://locations.cinnaholic.com/locations-list/"
        soup = bs(session.get(base_url, headers=_header1).text, "lxml")
        states = soup.select("div.content ul li a")
        for state in states:
            soup1 = bs(
                session.get(
                    f'https://locations.cinnaholic.com{state["href"]}', headers=_header1
                ).text,
                "lxml",
            )
            cities = soup1.select("div.content ul li a")
            for city in cities:
                soup3 = bs(
                    session.get(
                        f'https://locations.cinnaholic.com{city["href"]}',
                        headers=_header1,
                    ).text,
                    "lxml",
                )
                details = soup3.select("div.content ul li a")
                for detail in details:
                    page_url = detail["href"]
                    soup4 = bs(session.get(page_url, headers=_header1).text, "lxml")
                    addr = parse_address_intl(soup4.select_one("div.address").text)
                    hours = [
                        ": ".join(list(_.stripped_strings))
                        for _ in soup4.select("div.store-hours .hours-box .day-row")
                    ]
                    if soup4.h3.text not in names:
                        names.append(soup4.h3.text)
                    else:
                        continue

                    yield SgRecord(
                        page_url=page_url,
                        location_name=soup4.h3.text,
                        street_address=f"{addr.street_address_1} {addr.street_address_2}",
                        city=addr.city,
                        state=addr.state,
                        zip_postal=addr.postcode,
                        country_code="US",
                        phone=_phone(soup4.select_one("div.phone a").text),
                        locator_domain=locator_domain,
                        hours_of_operation=_valid("; ".join(hours)),
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
