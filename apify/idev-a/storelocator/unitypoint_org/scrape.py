from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("unitypoint")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

_header1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.unitypoint.org",
    "referer": "https://www.unitypoint.org/quadcities/find-a-location.aspx",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locator_domain = "https://www.unitypoint.org"
base_url = "https://www.unitypoint.org/quadcities/find-a-location.aspx"


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xae", " ")
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        __EVENTARGUMENT = soup.select_one("input#__EVENTARGUMENT")["value"]
        __VIEWSTATE = soup.select_one("input#__VIEWSTATE")["value"]
        __VIEWSTATEGENERATOR = soup.select_one("input#__VIEWSTATEGENERATOR")["value"]
        __EVENTVALIDATION = soup.select_one("input#__EVENTVALIDATION")["value"]
        data = {
            "__EVENTTARGET": "ctl00$kyruusLocationSearch$search",
            "__EVENTARGUMENT": __EVENTARGUMENT,
            "__VIEWSTATE": __VIEWSTATE,
            "ctl00$kyruusLocationSearch$name": "",
            "ctl00$kyruusLocationSearch$zip": "",
            "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
            "__EVENTVALIDATION": __EVENTVALIDATION,
        }
        sp1 = bs(session.post(base_url, headers=_header1, data=data).text, "lxml")
        locations = sp1.select("div.flex-module-list.location-list div.location-result")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = f"{locator_domain}{_.h3.a['href']}"
            logger.info(page_url)
            coord = (
                _.select_one('div[data-id="map"]')["style"]
                .split("center=")[1]
                .split("&zoom")[0]
                .split(",")
            )
            block = list(_.select_one('p[data-id="address"]').stripped_strings)
            street_address = block[0]
            if len(block) > 2:
                street_address = " ".join(block[:-1])
            state_zip = block[-1].split(",")[1].strip().split(" ")
            phone = _.select_one('a[data-id="phone"]').text
            with SgRequests() as session:
                soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hours = []
                for hour in soup1.select("table.data-list tr"):
                    hours.append(f"{hour.td.text}: {hour.select('td')[1].text}")
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.h3.a.text,
                    street_address=street_address,
                    city=block[-1].split(",")[0].strip(),
                    state=state_zip[0],
                    zip_postal=state_zip[1],
                    country_code="US",
                    phone=phone,
                    latitude=coord[0],
                    longitude=coord[1],
                    locator_domain=locator_domain,
                    hours_of_operation=_valid("; ".join(hours)),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
