from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://bluebottlecoffee.com/"
        base_url = "https://bluebottlecoffee.com/api/cafe_search/fetch.json?cafe_type=all&coordinates=false&query=true&search_value=all"
        r = session.get(base_url, headers=_headers).json()
        for q in r["cafes"]:
            for dt in r["cafes"][q]:
                latitude = dt["latitude"]
                longitude = dt["longitude"]
                name = dt["name"]
                address = bs(dt["address"], "lxml")
                full = list(address.stripped_strings)
                if "00000" in full:
                    continue
                if full[-1] == "Ttukseom station — exit #1":
                    del full[-1]
                if len(full[-1].split(",")) == 1:
                    del full[-1]

                city = full[-1].split(",")[0]
                zipp = full[-1].split(",")[-1].split()[-1]
                states = " ".join(full[-1].split(",")[-1].split()[:-1])
                if len(states) == 2:
                    addressses = " ".join(full[:-1])
                    addressses = addressses.replace(
                        "Entrance is on 52nd St", ""
                    ).replace("NW corner of Tower 4", "")
                    page_url = dt["url"]
                    r1 = session.get(page_url)
                    soup = bs(r1.text, "lxml")
                    hours = []
                    hours_of_operation = ""
                    for _ in soup.select("div.mw5.mw-100-ns div.dt.wi-100.pb10.f5"):
                        time = "".join(
                            [_t for _t in _.select_one("div.dtc.tr").stripped_strings]
                        )
                        hours.append(f"{_.select_one('div.dtc').text}: {time}")

                    if not hours:
                        if soup.find("div", {"class": "mw5 mw-100-ns"}):
                            hours_of_operation = soup.find(
                                "div", {"class": "mw5 mw-100-ns"}
                            ).text
                    else:
                        hours_of_operation = re.sub(
                            r"\s+", " ", "; ".join(hours)
                        ).strip()

                    if "reopened" in hours_of_operation:
                        hours_of_operation = ""
                    if "temporarily closed" in hours_of_operation:
                        hours_of_operation = "temporarily closed"
                    yield SgRecord(
                        page_url=page_url,
                        location_name=name,
                        street_address=addressses,
                        city=city,
                        state=states,
                        zip_postal=zipp,
                        country_code="US",
                        latitude=latitude,
                        longitude=longitude,
                        locator_domain=locator_domain,
                        hours_of_operation=_valid(hours_of_operation),
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
