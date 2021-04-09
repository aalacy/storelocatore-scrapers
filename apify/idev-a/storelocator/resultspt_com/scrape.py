from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def fetch_data():
    locator_domain = "https://www.resultspt.com"
    base_url = "https://www.resultspt.com/locations"
    with SgRequests() as session:
        sp = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = sp.select("div.location-column li a")
        for link in links:
            page_url = locator_domain + link["href"]
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in sp1.select("div.lmlw-hours-normal-wrap div"):
                temp = hh.select("span")
                time = temp[1].text
                if len(temp) == 4:
                    time = f"{temp[1].text}-{temp[3].text}"
                hours.append(f"{temp[0].text} {time}")
            with SgChrome(
                executable_path=r"/mnt/g/work/mia/chromedriver.exe"
            ) as driver:
                driver.get(page_url)
                import pdb

                pdb.set_trace()

                sp2 = bs(
                    session.get(sp1.select_one("iframe.lmlw-map__iframe")["src"]).text,
                    "lxml",
                )
                coord = (
                    sp2.select_one("div.google-maps-link a")["href"]
                    .split("ll=")[1]
                    .split("&z")[0]
                    .split(",")
                )
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.select_one("h1.lmlw-header__header").text,
                    street_address=sp1.select_one("span.lmlw-addr-wrap__address").text,
                    city=sp1.select_one("span.lmlw-addr-wrap__city").text,
                    state=sp1.select_one("span.lmlw-addr-wrap__state").text,
                    latitude=coord[0],
                    longitude=coord[1],
                    zip_postal=sp1.select_one("span.lmlw-addr-wrap__zip").text,
                    country_code="US",
                    phone=sp1.select_one("span.lmlw-contact-phone__number").text,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
