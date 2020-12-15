from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json


def para(k):
    results = []
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    url = k["url"]
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    scripts = soup.find_all("script")
    thescript = ""

    for i in scripts:
        if "PRELOADED_STATE" in i.text:
            thescript = i.text

    thescript = thescript.split("window.__APOLLO_STATE", 1)[-1]
    thescript = "{" + thescript.split("= {", 1)[1]
    thescript = thescript.split("ERROR_STATE", 1)[0]
    thescript = thescript.rsplit(";", 1)[0]
    thescript = json.loads(thescript)

    uniques = set()

    for i in list(thescript):
        if "FullWidthPanel_gb_en_" in i:
            dent = []
            for j in i:
                if j.isdigit():
                    dent.append(j)
            dent = "".join(dent)
            if dent not in uniques:
                uniques.add(dent)

    for i in uniques:
        store = {}
        for j in list(thescript):
            if i in j:
                store.update(thescript[j])

        store["page_url"] = url
        store["moredata"] = k
        results.append(store)

    for i in results:
        yield i


def parsed(k):
    nice = {}
    nice["url"] = k["page_url"]
    soup = b4(k["textBlock"], "lxml")

    try:
        nice["address"] = soup.find("p").text.strip()
    except Exception:
        nice["address"] = "<MISSING>"

    try:
        nice["city"] = nice["address"].split(",")[-3].strip()
    except Exception:
        nice["city"] = "<MISSING>"

    try:
        nice["state"] = nice["address"].split(",")[-2].strip()
    except Exception:
        nice["state"] = "<MISSING>"

    try:
        nice["zipcode"] = nice["address"].split(",")[-1].strip()
    except Exception:
        nice["zipcode"] = "<MISSING>"

    try:
        nice["latitude"] = k["URL"].split("/@", 1)[1].split("/")[0]
    except Exception:
        nice["latitude"] = "<MISSING>"

    try:
        nice["address"] = ", ".join(nice["address"].split(",")[0:-3])

    except Exception:
        nice["address"] = "<MISSING>"

    try:
        nice["id"] = k["id"]
    except Exception:
        nice["id"] = "<MISSING>"

    try:
        nice["phone"] = soup.find(
            "a", {"href": lambda x: x and x.startswith("tel:")}
        ).text.strip()
    except Exception:
        nice["phone"] = "<MISSING>"

    try:
        # hour data is NOT pretty. always a table that has minimum 2 columns, sometimes more: https://prnt.sc/vz66l4
        nice["hours"] = list(soup.find("tbody").stripped_strings)
        idex = 0
        types = []
        while "day" not in nice["hours"][idex]:
            types.append(nice["hours"][idex])
            nice["hours"].pop(idex)

        totaltypes = len(types)

        h = []

        for idex, val in enumerate(types):
            i = 0
            h.append(str(val) + " > ")
            while i < len(nice["hours"]):
                h.append(nice["hours"][i] + ": ")
                h.append(nice["hours"][i + idex + 1] + "; ")
                i += totaltypes
                i += 1
            if idex < totaltypes - 1:
                h.append("\n")

        nice["hours"] = "".join(h)

    except Exception:
        nice["hours"] = "<MISSING>"

    try:
        nice["hours"] = nice["hours"].split("\n")
    except Exception:
        nice["hours"] = [nice["hours"]]

    try:
        typ = []
        for i in nice["hours"]:
            typ.append(i.split(" >")[0])
        nice["type"] = ", ".join(typ)

    except Exception:
        nice["type"] = k["heading1"]

    try:
        nice["hours"] = nice["hours"][0].split(" >")[-1].strip()
    except Exception:
        nice["hours"] = nice["hours"][0]

    try:
        nice["longitude"] = nice["latitude"].split(",")[1].strip()
        nice["latitude"] = nice["latitude"].split(",")[0].strip()
    except Exception:
        nice["longitude"] = "<MISSING>"

    try:
        nice["name"] = k["heading2"]
    except Exception:
        nice["name"] = "<MISSING>"

    donesomething = 0
    try:
        zipfix = []
        extras = []
        for i in nice["zipcode"].split(" "):
            if len(i.strip()) == 2 or len(i.strip()) == 3 or len(i.strip()) == 4:
                if all(c.isdigit() or c.isupper() for c in i) or i == "iAJ":
                    zipfix.append(i)
                else:
                    extras.append(i)
            else:
                extras.append(i)
        nice["zipcode"] = " ".join(zipfix)
        while len(extras) > 0:
            if len(extras[0]) > 1:
                nice["address"] = nice["address"] + nice["city"]
                nice["city"] = nice["state"]
                nice["state"] = extras[0]
                nice["address"].replace("<MISSING>", "")
                looped = 0
                while len(nice["address"] < 3) and looped < 10:
                    nice["address"] = nice["address"] + nice["city"]
                    nice["city"] = nice["state"]
                    looped += 1
                    nice["address"].replace("<MISSING>", "")

                donesomething += 1
            extras.pop(0)
    except Exception:
        nice["zipcode"] = nice["zipcode"]
    if (len(nice["address"])) < 3:
        nice["address"] = "<MISSING>"

    if nice["address"] == "<MISSING>" and donesomething == 0:
        nice["address"] = soup.find("p").text.strip()
        nice["city"] = nice["state"]
        nice["state"] = "<MISSING>"
        nice["address"] = (
            nice["address"][::-1]
            .replace(nice["city"][::-1], ""[::-1], 1)[::-1]
            .replace(nice["state"][::-1], ""[::-1], 1)[::-1]
            .replace(nice["zipcode"][::-1], ""[::-1], 1)[::-1]
        )
    if donesomething > 0:
        nice["address"] = (
            nice["address"][::-1]
            .replace(nice["city"][::-1], ""[::-1], 1)[::-1]
            .replace(nice["state"][::-1], ""[::-1], 1)[::-1]
            .replace(nice["zipcode"][::-1], ""[::-1], 1)[::-1]
        )

    nice["morestuff"] = k
    nice["country"] = nice["id"].split("_", 1)[0]

    return nice


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")
    # https://www.mitsubishi-motors.co.uk/dealer-locator
    url = "https://www.mitsubishi-motors.co.uk/dealer-locator"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    scripts = soup.find_all("script")
    thescript = ""

    for i in scripts:
        if "PRELOADED_STATE" in i.text:
            thescript = i.text

    thescript = thescript.split("window.__APOLLO_STATE", 1)[-1]
    thescript = "{" + thescript.split("= {", 1)[1]
    thescript = thescript.split("ERROR_STATE", 1)[0]
    thescript = thescript.rsplit(";", 1)[0]
    thescript = json.loads(thescript)

    data = {}
    data["stores"] = []
    data["extras"] = {}
    data["final"] = []

    for key in list(thescript):
        if "Dealer_" in key:
            if ".phone" not in key and ".address" not in key:
                k = {}
                k = thescript[key]
                if k["phone"]["generated"]:
                    k["phone"] = thescript[k["phone"]["id"]]
                if k["address"]["generated"]:
                    k["address"] = thescript[k["address"]["id"]]
                data["stores"].append(k)

            else:
                data["extras"][key] = thescript[key]

    lize = utils.parallelize(
        search_space=data["stores"],
        fetch_results_for_rec=para,
        max_threads=20,
        print_stats_interval=20,
    )

    for i in lize:
        for j in i:
            data["final"].append(j)

    for i in data["final"]:
        k = parsed(i)
        if "MISSING" not in k["type"]:
            yield k

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        x = x.split(",")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def scrape():
    url = "https://www.mitsubishi-motors.co.uk/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["url"]),
        location_name=sp.MappingField(
            mapping=["name"], is_required=False, part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(
            mapping=["address"],
            is_required=False,
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        city=sp.MappingField(
            mapping=["city"], is_required=False, part_of_record_identity=True
        ),
        state=sp.MappingField(
            mapping=["state"], is_required=False, part_of_record_identity=True
        ),
        zipcode=sp.MappingField(
            mapping=["zipcode"], is_required=False, part_of_record_identity=True
        ),
        country_code=sp.MappingField(mapping=["country"], part_of_record_identity=True),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MappingField(mapping=["id"]),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(mapping=["type"], part_of_record_identity=True),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
