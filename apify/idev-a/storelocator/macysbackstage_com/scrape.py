from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.macysbackstage.com/"
    base_url = "https://stores.macysbackstage.com/"
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.c-location-grid-item"
        )
        for _ in locations:
            page_url = base_url + _.h5.a["href"]
            soup = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in json.loads(
                _.select_one("div.c-location-hours-today")["data-days"]
            ):
                intervals = []
                for ii in hh["intervals"]:
                    intervals.append(f"{ii['start']}-{ii['end']}")
                hours.append(f"{hh['day']}: {', '.join(intervals)}")

            yield SgRecord(
                page_url=page_url,
                location_name=_.h5.a["title"],
                street_address=_.select_one("span.c-address-street").text,
                city=_.select_one("span.c-address-city").text.replace(",", ""),
                state=_.select_one("span.c-address-state").text,
                latitude=soup.select_one('meta[itemprop="latitude"]')["content"],
                longitude=soup.select_one('meta[itemprop="longitude"]')["content"],
                zip_postal=_.select_one("span.c-address-postal-code").text,
                country_code="US",
                phone=_.select_one("a.c-phone-main-number-link").text,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
