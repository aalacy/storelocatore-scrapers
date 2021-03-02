from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import demjson

locator_domain = "https://www.qdstores.co.uk/"
base_url = "https://www.qdstores.co.uk/static/store-finder.html"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Referer": "https://www.qdstores.co.uk/",
    }


def _hoo(soup, number):
    hours = soup.select("div.opening-times")
    temp = []
    for _ in hours:
        if _["data-id"] == f"opening-{number}":
            keys = [t.text for t in _.select("dt")]
            values = [t.text for t in _.select("dd")]
            for tt in range(len(keys)):
                if keys[tt] in [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]:
                    temp.append(f"{keys[tt]}: {values[tt]}")
            return "; ".join(temp)


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        soup = bs(res.text, "lxml")
        body = (
            res.text.split("Stores =")[1]
            .strip()
            .split("// Initiates the class once the DOM is ready")[0]
            .strip()
        )
        json_data = (
            body.replace("\t", "").replace("\n", "").replace("\r", "")[:-3] + "}"
        )
        locations = demjson.decode(json_data)
        for key, _ in locations.items():
            street_address = "<MISSING>"
            city = "<MISSING>"
            zip_postal = "<MISSING>"
            phone = _["tel"]
            try:
                addr = _["address"].split("<br />")
                street_address = " ".join(addr[:-2])
                city = addr[-2]
                if city.replace(" ", "").isdigit():
                    phone = city
                    city = addr[-3]
                zip_postal = addr[-1]
            except:
                pass
            record = SgRecord(
                page_url="https://www.qdstores.co.uk/static/store-finder.html",
                store_number=_["number"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                country_code="uk",
                latitude=_["lat"],
                longitude=_["lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_hoo(soup, _["number"]),
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
