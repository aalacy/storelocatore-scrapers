from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape.simple_scraper_pipeline import MissingField
from bs4 import BeautifulSoup as b4
from sgrequests import SgRequests
import json


def fetch_data():
    with SgRequests() as session:
        url = "https://locations.geisinger.org/?utm_source=Locations%20Page&utm_medium=Web&utm_campaign=Locations%20CTA"
        soup = session.get(url)
        # json location
        soup = b4(soup.text, "lxml")
        k = soup.find("div", {"id": "bottom"}).find("script").text.strip()
        k = k.split("var results= ")[1]
        k = k.split("[", 1)[1]
        k = k.split("}];")[0]
        k = '{"stores":[' + k + "}]}"
        son = json.loads(k)
        for i in son["stores"]:
            soup = session.get(
                str(
                    "https://locations.geisinger.org/details.cfm?id="
                    + str(i["CLINICID"])
                )
            )
            backup = soup.text.replace("<b>", '"').replace("</b>", '"')
            soupy = b4(backup, "lxml")
            soup = b4(soup.text, "lxml")
            try:
                i["hours"] = "; ".join(
                    list(
                        soup.find("div", {"class": "officeHours"})
                        .find("p")
                        .stripped_strings
                    )
                )
            except Exception:
                try:
                    i["hours"] = "; ".join(
                        list(
                            soup.find("div", {"class": "officeHours"}).stripped_strings
                        )
                    )
                except Exception:
                    try:
                        i["hours"] = soup.find(
                            "div", {"class": "officeHours"}
                        ).text.strip()
                    except Exception:
                        i["hours"] = "<MISSING>"
            old = i["hours"]
            soup = soupy
            try:
                i["hours"] = "; ".join(
                    list(
                        soup.find("div", {"class": "officeHours"})
                        .find("p")
                        .stripped_strings
                    )
                )
            except Exception:
                try:
                    i["hours"] = "; ".join(
                        list(
                            soup.find("div", {"class": "officeHours"}).stripped_strings
                        )
                    )
                except Exception:
                    try:
                        i["hours"] = soup.find(
                            "div", {"class": "officeHours"}
                        ).text.strip()
                    except Exception:
                        i["hours"] = "<MISSING>"

            i["hours"] = old.replace(":;", "")
            try:
                coords = soup.find("", {"href": lambda x: x and "maps" in x})["href"]
                coords = coords.split("/@", 1)[1].split("/", 1)[0].split(",")
            except Exception:
                coords = ["<INACCESSIBLE>", "<INACCESSIBLE>"]

            if coords[0] == "<INACCESSIBLE>":
                try:
                    coords = (
                        i["OFFICEHOURS"]
                        .split("href", 1)[1]
                        .split("maps", 1)[1]
                        .split("@", 1)[1]
                        .split("/", 1)[0]
                        .split(",")
                    )
                except Exception:
                    coords = ["<INACCESSIBLE>", "<INACCESSIBLE>"]
            i["lon"] = coords[1]
            i["lat"] = coords[0]
            try:
                i["hours"] = i["hours"].split(";")
                h = []
                for j in i["hours"]:
                    if (
                        any(
                            i in j
                            for i in [
                                "day",
                                "p.m.",
                                "a.m.",
                                ":",
                                "aci",
                                "ine",
                                "ory",
                                "ics",
                            ]
                        )
                        and any(i not in j for i in ["ppointment", "call"])
                    ):
                        h.append(j)

                i["hours"] = "; ".join(h)
                i["hours"] = i["hours"].replace("\r", ";").replace("\n", ";")
                i["hours"] = i["hours"].replace(";;", ";")
                i["hours"] = i["hours"].replace(";;", ";")
            except Exception:
                i["hours"] = i["hours"]

            try:
                i["ADDRESS2"] = i["ADDRESS2"]
            except Exception:
                i["ADDRESS2"] = ""
            yield i


def parse_features(x):
    s = b4(str(x), "lxml")
    s = "; ".join(list(s.stripped_strings))
    s = s.replace("\n", ";").replace("\r", ";").replace(";;", ";").replace(";;", ";")
    copy = ""
    while "<!" in s:
        try:
            copy = copy + " " + str(s.split("<!")[0])
            copy = copy + " " + str(s.split("-->")[1])
        except Exception:
            return copy
        if "<!" not in copy:
            s = copy

    return s


def fix_address(x):

    flag = 0
    unwanted = ["Markets", "Plaza", "Center", "Hospital", "FLoor", "Clinic"]
    isdigit = [0, 0]
    h = []
    added = [0, 0]

    for i in range(len(x)):
        if any(j.isdigit() for j in x[i]):
            isdigit[i] = 1
        if "Level 2:" in x[i]:
            x[i] = x[i].split("Level 2:", 1)[1].strip()
    for i in range(len(x)):
        if any(j in x[i] for j in unwanted):
            flag += 1
            if i == 0:
                if isdigit[0] == 1:
                    h.append(x[0])
                    added[0] = 1
                if len(x[1]) > 3 and isdigit[1] == 1:
                    if added[1] == 0:
                        h.append(x[1])
                        added[1] = 1
                else:
                    if added[0] == 0:
                        h.append(x[0])
                        added[0] = 1
            if i == 1 and added[0] == 0:
                h.append(x[0])
                added[0] = 1
        else:
            if added[i] == 0:
                h.append(x[i])
                added[i] = 1
    if flag > 0:
        for i in range(len(h)):
            try:
                h[i] = fix_address(h[i].split(",", 1))
            except Exception:
                h[i] = h[i]
    h = " ".join(h).replace("<br>", " ").strip()

    return h


def scrape():
    url = "https://www.geisinger.org/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["CLINICID"],
            value_transform=lambda x: "https://locations.geisinger.org/details.cfm?id="
            + str(x),
        ),
        location_name=MappingField(
            mapping=["NAME"], value_transform=lambda x: x.replace("&amp; ", "")
        ),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lat"]),
        street_address=MultiMappingField(
            mapping=[["ADDRESS1"], ["ADDRESS2"]], raw_value_transform=fix_address
        ),
        city=MappingField(mapping=["CITY"]),
        state=MappingField(mapping=["STATE"]),
        zipcode=MappingField(
            mapping=["ZIPCODE"],
            value_transform=lambda x: x.replace(" ", "").replace("*", ""),
            is_required=False,
        ),
        country_code=MissingField(),
        phone=MappingField(mapping=["PHONE"], is_required=False),
        store_number=MappingField(mapping=["CLINICID"]),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MappingField(
            mapping=["OTHERSERVICES"], value_transform=parse_features, is_required=False
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="scr",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
