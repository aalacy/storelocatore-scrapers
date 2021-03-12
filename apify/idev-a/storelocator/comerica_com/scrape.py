from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import us

_headers = {
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


def fetch_data():
    urls = []
    with SgRequests() as session:
        locator_domain = "https://www.comerica.com/"
        for _state in us.states.STATES:
            page = 1
            while True:
                base_url = f"https://locations.comerica.com/?q={_state.abbr.lower()}&filter=all&page={page}"
                soup = bs(session.get(base_url, headers=_headers).text, "lxml")
                if not soup.select_one("ul.pager li.pager-current span"):
                    break
                locations = soup.select("#results-list a")
                for link in locations:
                    if not link["href"].startswith("https"):
                        continue
                    if link["href"] in urls:
                        continue
                    urls.append(link["href"])

                    soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
                    hours = []
                    for tr in soup1.select("div.open-hours-lobby tr"):
                        hours.append(
                            f"{tr.select('td')[0].text}: {tr.select('td')[1].text}"
                        )
                    city = state = zip_postal = phone = ""
                    country_code = "US"
                    if soup1.select_one("div.adr span.locality"):
                        city = soup1.select_one("div.adr span.locality").text
                    if soup1.select_one("div.adr span.region"):
                        state = soup1.select_one("div.adr span.region").text
                    if soup1.select_one("div.adr span.postal-code"):
                        zip_postal = soup1.select_one("div.adr span.postal-code").text
                    if soup1.select_one("div.adr div.country-name"):
                        country_code = soup1.select_one("div.adr div.country-name").text
                    if soup1.select_one('div.tel span[property="telephone"]'):
                        phone = soup1.select_one(
                            'div.tel span[property="telephone"]'
                        ).text
                    yield SgRecord(
                        store_number=link["data-location-id"],
                        page_url=link["href"],
                        location_name=link.select_one("div.result-title").text.strip(),
                        street_address=soup1.select_one(
                            "div.adr div.street-address"
                        ).text,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code=country_code,
                        latitude=soup1.select_one("abbr.latitude")["content"],
                        longitude=soup1.select_one("abbr.longitude")["content"],
                        phone=phone,
                        locator_domain=locator_domain,
                        hours_of_operation=_valid("; ".join(hours)),
                    )

                cur_page = int(
                    soup.select_one("ul.pager li.pager-current span")
                    .text.split("of")[-1]
                    .strip()
                )
                page += 1
                if page > cur_page:
                    break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
