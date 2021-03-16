from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import demjson

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.becksprime.com"
        base_url = "https://www.becksprime.com/locations/"
        r = session.get(base_url, headers=_headers, verify=False)
        soup = bs(r.text, "html.parser")
        locations = soup.select("section.locations-list div.locations")
        for _ in locations:
            _addr = list(_.select("div.group .grid-item")[0].stripped_strings)
            _hour = list(_.select("div.group .grid-item")[1].stripped_strings)
            state_zip = _addr[1].split(",")[1].strip()
            page_url = locator_domain + _.h4.a["href"]
            res = session.get(page_url, headers=_headers).text
            lat_lng = demjson.decode(
                res.split("var heights =")[1]
                .strip()
                .split("var mapStyles =")[0]
                .strip()[:-1]
            )
            latitude = lat_lng["lat"]
            longitude = lat_lng["lng"]

            yield SgRecord(
                page_url=page_url,
                location_name=_.h4.text,
                street_address=_addr[0],
                city=_addr[1].split(",")[0],
                state=state_zip.split(" ")[0],
                zip_postal=state_zip.split(" ")[-1],
                country_code="US",
                phone=_hour[0],
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(_hour[1:])),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
