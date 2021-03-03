from sgscrape import simple_scraper_pipeline as sp
from sgscrape import sgpostal as parser
from sglogging import sglog

from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def good_luck(soup):
    data = soup.find("tbody").find_all("tr")
    h = []
    h.append([])
    iterData = 0
    while iterData < len(data):
        if iterData == 0:
            tops = data[iterData].find_all("th")
            for i in tops:
                h[0].append(" ".join(list(i.stripped_strings)))
        else:
            h.append(list(data[iterData].stripped_strings))
        iterData += 1
    hours = None
    width = len(h[0]) - 1
    iterWide = 1
    while iterWide < width:
        iterLength = 0
        h2 = []
        while iterLength < len(h):
            if iterLength != 0:
                h2.append(h[iterLength][0] + ": " + h[iterLength][iterWide] + ", ")
            else:
                h2.append(h[iterLength][iterWide] + ": ")
            iterLength += 1
        iterWide += 1
        if not hours:
            hours = "".join(h2)
        else:
            hours = hours + "; " + "".join(h2)

    return hours.replace(", ;", ";")


def mostly_numbers(x):
    total = len(x)
    digits = 0
    if total > 10 and total < 13:
        for i in x:
            if i.isdigit() or i == "-":
                digits += 1
    percentage = round((digits / total * 100), 2)
    return percentage


def figure_out(first, second):
    k = {}
    try:
        k["name"] = first.find("h5").text.strip()
    except Exception:
        k["name"] = "<MISSING>"

    if k["name"] == "<MISSING>":
        try:
            k["name"] = first.find("h2").text.strip()
        except Exception:
            k["name"] = "<MISSING>"

    raw_addr = list(
        second.find(
            "div",
            {"class": lambda x: x and all(i in x for i in ["hidden-xs", "hidden-sm"])},
        )
        .find("p")
        .stripped_strings
    )

    z = 0
    length_raw = len(raw_addr)
    undesirables = [
        "all branches",
        "lease note",
        "branch lobbies",
        "et directions",
        "temporarily closed",
        "pecial alert",
    ]
    while z < length_raw:
        if any(i in raw_addr[z] for i in undesirables):
            raw_addr.pop(z)
            length_raw += -1
            z += -1
        z += 1
    # pops the 'Get directions' text and the phone number and other unwanted crap
    raw_addr = " ".join(raw_addr)
    if "S. Dartmouth" in raw_addr:
        raw_addr = raw_addr.replace("S. Dartmouth", "Dartmouth")
    if k["name"] != "<MISSING>" and "," in k["name"]:
        raw_addr = raw_addr + "," + k["name"]
    k["raw_addr"] = raw_addr

    parsed = parser.parse_address_usa(raw_addr)
    k["country"] = parsed.country if parsed.country else "<MISSING>"
    k["state"] = parsed.state if parsed.state else "<MISSING>"
    k["postcode"] = parsed.postcode if parsed.postcode else "<MISSING>"
    k["city"] = parsed.city if parsed.city else "<MISSING>"
    k["street_address"] = (
        parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
    )
    k["street_address"] = (
        k["street_address"] + "," + parsed.street_address_2
        if parsed.street_address_2
        else k["street_address"]
    )

    if "Unit 02747" in k["street_address"]:
        k["street_address"] = k["street_address"].replace(",Unit 02747", "")
        k["postcode"] = "02747"

    k["hours"] = good_luck(second)
    find_phone = second.find_all("p", {"class": "location-desc"})
    h = []
    for i in find_phone:
        z = list(i.stripped_strings)
        for j in z:
            h.append(j)

    k["phone"] = ""
    for i in h:
        if mostly_numbers(i) > 90:
            k["phone"] = i
            break

    return k


def para(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")
    data = soup.find("div", {"class": "editor"})
    first = data.find_all(
        "div",
        {
            "class": lambda x: x
            and all(i in x for i in ["visible-xs-block", "visible-sm-block"])
        },
    )
    second = data.find_all("div", {"class": "row"})
    total = len(first)
    iterFirst = 0
    iterSecond = 0
    while iterFirst < total:
        try:
            z = figure_out(first[iterFirst], second[iterSecond])
        except Exception:
            try:
                iterSecond += 1
                z = figure_out(first[iterFirst], second[iterSecond])
                # I am SO SO SO SORRY for the code here.
            except Exception:
                raise Exception

        z["url"] = url
        yield z
        iterFirst += 1
        iterSecond += 1
        iterSecond += 1


def fetch_data():
    para("https://www.baycoastbank.com/home/locations/fallriverma")

    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.baycoastbank.com/home/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    links = (
        soup.find("div", {"class": "editor"})
        .find("div", {"class": "row"})
        .find_all("a")
    )
    pages = []
    for i in links:
        pages.append(str("https://www.baycoastbank.com" + i["href"]))

    lize = utils.parallelize(
        search_space=pages,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        for j in i:
            yield j

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.baycoastbank.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["url"],
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MissingField(),
        longitude=sp.MissingField(),
        street_address=sp.MappingField(
            mapping=["street_address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["postcode"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
        ),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
        ),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(
            mapping=["raw_addr"],
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
