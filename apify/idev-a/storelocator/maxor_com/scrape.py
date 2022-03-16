from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return (
        val.replace(")", "")
        .replace("(", "")
        .replace("-", "")
        .replace(" ", "")
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://maxsource.maxor.com/"
    base_url = "https://maxsource.maxor.com/pharmacy/locations.aspx"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("table#pharmacies tbody tr")
        for _ in locations:
            td = _.select("td")
            hours = list(td[-1].stripped_strings)
            if hours and not hours[0].startswith("Mon"):
                del hours[0]
            coord = td[1].a["href"].split("&ll=")[1].split("&s")[0].split(",")
            phone = list(td[5].stripped_strings)[0]
            if not _phone(phone):
                phone = list(td[5].stripped_strings)[1]
            yield SgRecord(
                page_url=base_url,
                location_name=" ".join(list(td[0].stripped_strings)),
                street_address=" ".join(list(td[1].stripped_strings)),
                city=td[2].text,
                state=td[3].text,
                zip_postal=td[4].text,
                country_code="US",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("  ", ""),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
