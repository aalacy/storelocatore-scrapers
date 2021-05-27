from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

locator_domain = "https://www.wellsfargo.com/"
base_url = "https://www.wellsfargo.com/locator/"
payload_url = "https://www.wellsfargo.com/locator/as/getpayload"
sitemap1 = "https://www.wellsfargo.com/locator/sitemap1"
sitemap2 = "https://www.wellsfargo.com/locator/sitemap2"

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "www.wellsfargo.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

session = SgRequests()


def parallel_run_one(link):
    session.get(link, headers=_headers)
    locations = session.post(payload_url, headers=_headers).json()["searchResults"]

    for _ in locations:

        page_url = f"https://www.wellsfargo.com/locator/bank/?slindex={_['index']}"
        hours_of_operation = "; ".join(_.get("arrDailyEvents", []))
        if (
            "incidentMessage" in _
            and _["incidentMessage"].get("incidentDesc", "").lower()
            == "temporary closure"
            and _["incidentMessage"].get("outletStatusDesc", "").lower() == "closed"
        ):
            hours_of_operation = "Temporary closed"

        yield [
            page_url,
            _["branchName"],
            _["locationLine1Address"],
            _["city"],
            _["state"],
            _["postalcode"],
            "US",
            _["latitude"],
            _["longitude"],
            _["locationType"],
            _["phone"].strip(),
            locator_domain,
            hours_of_operation,
            "<MISSING>",
        ]


def scrape_loc_urls(location_urls):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(parallel_run_one, link) for link in location_urls]
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    yield record
            except Exception:
                pass


def scrape_loc_urls_two(location_urls):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(parallel_run_two, link) for link in location_urls]
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    yield record
            except Exception:
                pass


def parallel_run_two(link):
    res = session.get(link, headers=_headers)
    if "error.html" in res.url:
        return None
    sp1 = bs(res.text, "lxml")
    if sp1.find("", string=re.compile(r"could not find")):
        return None
    location_type = sp1.select_one("div.fn.heading").text.strip()
    if "ATM" not in location_type:
        return None
    try:
        coord = (
            sp1.select_one("div.mapView img")["src"]
            .split("Road/")[1]
            .split("/")[0]
            .split(",")
        )
    except:
        coord = ["", ""]
    hours = []
    _hr = sp1.find("h2", string=re.compile(r"Lobby Hours", re.IGNORECASE))
    if _hr:
        hours = list(_hr.find_next_sibling().stripped_strings)
    addr = [aa for aa in list(sp1.address.stripped_strings) if aa.strip() != ","]
    street_address = " ".join(addr[1].split(",")[:-1])
    yield [
        link,
        addr[0],
        street_address,
        addr[1].split(",")[-1],
        addr[2],
        addr[3],
        "US",
        coord[0],
        coord[1],
        location_type,
        sp1.find("a", href=re.compile(r"tel:")).text.strip(),
        locator_domain,
        "; ".join(hours),
        "<MISSING>",
    ]


def fetch_data():

    # sitemap1
    links = bs(session.get(sitemap1).text, "lxml").text.strip().split("\n")
    results = scrape_loc_urls(links)

    for result in results:
        for item in result:
            yield item

    # sitemap2
    links = (
        bs(session.get(sitemap2, headers=_headers).text, "lxml")
        .text.strip()
        .split("\n")
    )
    results = scrape_loc_urls_two(links)

    for result in results:
        for item in result:
            yield item


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "latitude",
                "longitude",
                "location_type",
                "phone",
                "locator_domain",
                "hours_of_operation",
                "store_number",
            ]
        )
        # Body
        streets = []
        for row in data:

            street_check = row[2]
            if street_check in streets:
                continue
            else:
                streets.append(street_check)

            final_row = []
            for item in row:
                if item == "":
                    final_row.append("<MISSING>")
                else:
                    final_row.append(item)
            writer.writerow(final_row)


if __name__ == "__main__":

    results = fetch_data()
    write_output(results)
