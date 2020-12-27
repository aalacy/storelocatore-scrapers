from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def para(url):

    url1 = "https://www.securitas.ca"
    empty = True
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url1 + url, headers=headers)
    soup = b4(son.text, "lxml")
    data = soup.find("div", {"class": "office-page"})

    k = {}

    try:
        stuff = data.find_all("div", {"class": "item"})
    except:
        k["Error"] = True
        k["CustomUrl"] = url
        return k
    k["CustomUrl"] = url1 + url

    try:
        k["Latitude"] = data.find("div", {"class": "office-map"}).find(
            "img", {"src": True, "class": "img-responsive"}
        )["src"]
        k["Latitude"] = k["Latitude"].split("center=")[1].split("&", 1)[0].split(",")[0]
        empty = False
    except:
        k["Latitude"] = "<MISSING>"

    try:
        k["Longitude"] = data.find("div", {"class": "office-map"}).find(
            "img", {"src": True, "class": "img-responsive"}
        )["src"]
        k["Longitude"] = (
            k["Longitude"].split("center=")[1].split("&", 1)[0].split(",")[1]
        )
        empty = False
    except:
        k["Longitude"] = "<MISSING>"

    try:
        k["Name"] = soup.find("h1", {"class": "page-title"}).text.strip()
    except:
        k["Name"] = "<MISSING>"

    try:
        k["Address"] = "<MISSING>"
        for i in stuff:
            if "Address:" in i.text:
                k["Address"] = i.text.split("Address:")[1].strip()
                empty = False
    except:
        k["Address"] = "<MISSING>"

    try:
        k["City"] = "<MISSING>"
        for i in stuff:
            if "Town:" in i.text:
                k["City"] = i.text.split("Town:")[1].strip()
                empty = False
        empty = False
    except:
        k["City"] = "<MISSING>"

    try:
        k["State"] = "<MISSING>"
        for i in stuff:
            if "vince:" in i.text:
                k["State"] = i.text.split("vince:")[1].strip()
                empty = False
    except:
        k["State"] = "<MISSING>"

    try:
        k["Zip"] = "<MISSING>"
        for i in stuff:
            if "ode:" in i.text:
                k["Zip"] = i.text.split("ode:")[1].strip()
                empty = False
    except:
        k["Zip"] = "<MISSING>"

    try:
        k["Phone"] = "<MISSING>"
        for i in stuff:
            if "Phone:" in i.text:
                k["Phone"] = i.text.split("Phone:")[1].strip()
                try:
                    k["Phone"] = k["Phone"].split("/")[0].strip()
                except:
                    k["Phone"] = k["Phone"]
                empty = False
        empty = False
    except:
        k["Phone"] = "<MISSING>"

    k["OpenHours"] = "<MISSING>"

    k["Country"] = "<MISSING>"
    k["IsActive"] = "<MISSING>"

    k["Error"] = empty
    return k


def fetch_data():
    para("/contact-us-offices/manitoba/winnipeg/")
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.securitas.ca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = son.text
    states = []  # noqa
    cities = []
    stores = []  # noqa

    soup = b4(soup, "lxml")
    data = soup.find_all(
        "div",
        {"class": lambda x: x and all(i in x for i in ["sub-pages", "dropdown-menu"])},
    )
    pages = ""
    for i in data:
        if "Contact" in i.text:
            pages = i

    data = pages.find_all(
        "a", {"href": lambda x: x and x.startswith("/contact-us-offices/")}
    )
    for i in data:
        cities.append(i["href"])

    lize = utils.parallelize(
        search_space=cities,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    issues = []

    for i in lize:
        if i["Error"]:
            issues.append(i["CustomUrl"])
        else:
            yield i
    total_issues = 0  # noqa
    final_issues = []
    logzilla.info(
        f"Sorting {len(issues)} issues..\n============================"
    )  # noqa
    url = "https://www.securitas.ca"

    for i in issues:
        if str(url + i).count("/") > 5:
            k = para(i)
            if not k["Error"]:
                yield k
            else:
                if str(url + i).count("/") > 5:
                    final_issues.append(str(url + i))
                    logzilla.info(f"============================")  # noqa
                    logzilla.info(f"=!!!!!!!!!!!!!!!!!!!!!!!!!!=")  # noqa
                    logzilla.info(
                        f"Could not figure out this url: \n\n{url+i}\n"
                    )  # noqa
                    logzilla.info(f"(Likely because page has no data)")  # noqa
                    logzilla.info(f"=!!!!!!!!!!!!!!!!!!!!!!!!!!=")  # noqa
                    logzilla.info(f"============================\n\n")  # noqa

    known_issues = [
        "https://www.securitasinc.com/Contact-Us/District-of-Columbia/",
        "https://www.securitasinc.com/Contact-Us/California/law-enforcement-division-special-projects-group/",
    ]

    known_issues.sort()
    final_issues.sort()

    for i in final_issues:
        damn = True
        for j in known_issues:
            if i == j:
                damn = False
        if damn:
            raise Exception(
                "Found an unexpected issue with url:",
                i,
                'If this is a non-issue please add the URL to the "known_issues" list:',
                known_issues,
            )  # noqa

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def pretty_hours(k):
    h = []

    if k != "<MISSING>":
        for i in k["days"]:
            try:
                h.append(
                    i["day"]
                    + ": "
                    + str(i["intervals"][0]["start"])
                    + "-"
                    + str(i["intervals"][0]["end"])
                )
            except:
                h.append(i["day"] + ": " + str("Closed"))

        h = "; ".join(h)
    else:
        h = k

    return h


def scrape():
    url = "https://www.securitas.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["CustomUrl"]),
        location_name=MappingField(
            mapping=["Name"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        latitude=MappingField(mapping=["Latitude"]),
        longitude=MappingField(mapping=["Longitude"]),
        street_address=MappingField(
            mapping=["Address"], value_transform=fix_comma, part_of_record_identity=True
        ),
        city=MappingField(
            mapping=["City"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        state=MappingField(
            mapping=["State"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        zipcode=MappingField(
            mapping=["Zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
            part_of_record_identity=True,
        ),
        country_code=ConstantField("CA"),
        phone=MappingField(
            mapping=["Phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
            part_of_record_identity=True,
        ),
        store_number=MissingField(),
        hours_of_operation=MappingField(
            mapping=["OpenHours"], raw_value_transform=pretty_hours, is_required=False
        ),
        location_type=MappingField(mapping=["IsActive"], is_required=False),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="securitas.ca",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
