from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.shaw.ca/"
base_url = "https://support.shaw.ca/t5/billing-account-articles/shaw-retail-locations/ta-p/5183#content-section-0"

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        tables = soup.select("div.tkb-content-box table")
        for table in tables:
            for _ in table.select("tr"):
                city = _.select("td")[0].p.text.strip()
                addr = list(_.select("td")[1].stripped_strings)
                if "Located across" in addr[-1]:
                    del addr[-1]
                if "Trans-Canada Hwy" in addr[-2]:
                    del addr[-2]
                hours = list(_.select("td")[2].stripped_strings)
                if "This location has temporarily relocated" in hours[0]:
                    del hours[0]
                if hours[0].startswith("This location follows"):
                    hours = []
                for x, hh in enumerate(hours):
                    if "Shaw Tower" in hh or "This location offers" in hh:
                        hours[x:] = []
                if hours and hours[0] == "Map and Hours":
                    hours = []
                coord = ["", ""]
                try:
                    coord = (
                        _.select("td")[2]
                        .a["href"]
                        .split("/@")[1]
                        .split("/data")[0]
                        .split(",")
                    )
                except:
                    pass
                yield SgRecord(
                    page_url=base_url,
                    location_name=city,
                    street_address=addr[-2],
                    city=city,
                    zip_postal=addr[-1],
                    country_code="CA",
                    locator_domain=locator_domain,
                    latitude=coord[0],
                    longitude=coord[1],
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
