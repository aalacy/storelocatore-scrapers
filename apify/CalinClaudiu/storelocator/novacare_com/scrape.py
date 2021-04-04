from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgrequests import SgRequests
from sglogging import sglog


def determine_brand(x):
    brands = {
        "Banner Physical Therapy": "https://resources.selectmedical.com/logos/op/Banner-PT-logo.png",
        "Emory Rehabilitation Outpatient Center": "https://resources.selectmedical.com/logos/op/Emory-Rehab-OP.png",
        "POSI - Prosthetic Orthotic Solutions International": "https://resources.selectmedical.com/logos/op/POSI-signage.png",
        "Kessler Rehabilitation Center": "https://resources.selectmedical.com/logos/op/OP_Kessler-Rehabilitation-Center.png",
        "PennState Health Rehabilitation Hospital": "https://resources.selectmedical.com/logos/op/PennState-Health-logo.png",
        "NovaCareKIDS Pediatric Therapy": "https://resources.selectmedical.com/logos/op/NovaCareKids-logo.png",
        "Kort": "https://resources.selectmedical.com/logos/op/brand-kort(1).png",
        "SSMHealth": "https://resources.selectmedical.com/logos/op/OP_SSMHealth-DayInstitute.png",
        "BaylorScott & White - Institute for Rehabilitaiton": "https://resources.selectmedical.com/logos/op/Baylor-Scott-White-logo.png",
        "NovaCare - Ohio Health": "https://resources.selectmedical.com/logos/op/OhioHealth-logo.png",
        "Physio": "https://resources.selectmedical.com/logos/op/Physio-Logo_MR-Small.png",
        "RushKIDS Pediatric Therapy": "https://resources.selectmedical.com/logos/op/RUSHKids-logo.png",
        "SelectKIDS Pediatric Therapy": "https://resources.selectmedical.com/logos/op/SelectKids-logo.png",
        "SACO BAY Orthopaedic & Sports": "https://resources.selectmedical.com/logos/op/SacoBay-4cLogoNoTag.png",
        "NovaCare Rehabilitation (wellspan)": "https://resources.selectmedical.com/logos/op/OP_wellspan-logo.png",
        "UnityPoint Health Marshalltown": "https://resources.selectmedical.com/logos/op/UnityPoint-Health-Marshalltown-logo.png",
        "CRI": "https://resources.selectmedical.com/logos/op/CRI-logo.png",
        "NovaCare Prostetics & Orthotics": "https://resources.selectmedical.com/logos/op/OP_NovaCare-PO-logo.png",
        "SSM Health Physical Therapy": "https://resources.selectmedical.com/logos/op/OP_SSMHealth-Physical-Therapy.png",
        "PennState Hereshey Rehabilitation Hospital": "https://resources.selectmedical.com/logos/op/REHAB_PennState-Rehabilitation-Hospital---USE-THIS-IN-THE-SCROLL.png",
        "West Gables Rehabilitation Hospital": "https://resources.selectmedical.com/logos/op/REHAB_West-Gables-Rehab-Hosp.png",
        "LifeBridge Health": "https://resources.selectmedical.com/logos/op/OP_NovaCare-LifeBridge.png",
        "Select Physical Therapy": "https://resources.selectmedical.com/logos/op/OP_Select-Physical-Therapy---USE-THIS-ONE-ON-THE-SCROLL.png",
        "Banner CHILDREN'S Physical Therapy": "https://resources.selectmedical.com/logos/op/BannerChildrensPT-logo.png",
        "Rehab ASSOCIATES": "https://resources.selectmedical.com/logos/op/RehabAssociates-logo.png",
        "SSM Health Day Institute": "https://resources.selectmedical.com/logos/op/SSM-Health-Day-Institute.png",
        "RUSH Physical Therapy": "https://resources.selectmedical.com/logos/op/RUSHPT-logo.png",
        "NovaCare Rehabilitation": "https://resources.selectmedical.com/logos/op/brand-novacare.png",
        "CSM - Champion Sports Medicine": "https://resources.selectmedical.com/logos/op/ChampionSportsMed-logo.png",
    }
    for brand, link in brands.items():
        if link in x:
            return brand

    try:
        x = x.split("img='", 1)[1].split("'", 1)[0]
        return x
    except Exception:
        pass
    return "<MISSING>"


def pretty_hours(x):
    x = x.replace("</td><td>", " ")
    x = x.replace("</tr>", ", ")
    x = x.replace("<tr>", "")
    x = x.replace("<td>", "")
    x = x.replace("</td>", "")
    if len(x) < 3:
        x = "<MISSING>"
    return x


def parse_html(x):
    k = {}
    j = []
    try:
        latlon = x.split("https://www.google.com/maps/search/?api=1&query=", 1)[
            1
        ].split("'", 1)[0]
        k["lat"] = latlon.split(",")[0]
        k["long"] = latlon.split(",")[1]
    except:
        k["lat"] = "<MISSING>"
        k["long"] = "<MISISNG>"
    add = (
        x.split("loc-result-card-address-container")[1]
        .split("'_blank'>")[1]
        .split("</a>", 1)[0]
    )
    # name
    try:
        k["name"] = (
            x.split("loc-result-card-name")[1]
            .split("<a href=")[1]
            .split(">")[1]
            .split("<", 1)[0]
        )
    except:
        k["name"] = "<MISSING>"
    # street address
    try:
        k["address"] = add.split("<br/>")
        for i in k["address"]:
            if i.count(",") != 1:
                j.append(i)
        k["address"] = ", ".join(j)
    except:
        k["address"] = "<MISSING>"

    # city
    try:
        k["city"] = add.split("<br/>")[-1].split(",", 1)[0]
    except:
        k["city"] = "<MISSING>"

    # state
    try:
        k["state"] = add.split("<br/>")[-1].split(",", 1)[1].split(" ")[1]
    except:
        k["state"] = "<MISSING>"

    # zip
    try:
        k["zip"] = add.split("<br/>")[-1].split(",", 1)[1].split(" ")[-1]
    except:
        k["zip"] = "<MISSING>"

    # phone
    try:
        k["phone"] = (
            x.split("loc-result-card-phone-container")[1].split("tel:")[1].split('"')[0]
        )
    except:
        k["phone"] = "<MISSING>"
    # hours
    try:
        k["hours"] = pretty_hours(
            x.split("mobile-container field-businesshours")[1]
            .split("<table>")[1]
            .split("</table>")[0]
        )
    except:
        k["hours"] = "<MISSING>"

    # type
    k["type"] = determine_brand(x.split("loc-result-card-logo")[1].split("</div>")[0])

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="novacare")
    url = "https://www.novacare.com//sxa/search/results/?s=&itemid={891FD4CE-DCBE-4AA5-8A9C-539DF5FCDE97}&sig=&autoFireSearch=true&v=%7B80D13F78-0C6F-42A0-A462-291DD2D8FA17%7D&p=3000&g=&o=Distance%2CAscending&e=0"

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    session = SgRequests()
    logzilla.info(f"Making API request.. this may take up to one minute")  # noqa
    son = session.get(url, headers=headers).json()
    logzilla.info(f"Finished request")  # noqa
    for i in son["Results"]:
        store = {}
        store["dic"] = i
        store["parsed"] = parse_html(i["Html"])
        if (
            store["dic"]["Geospatial"]["Latitude"] == 0
            or store["dic"]["Geospatial"]["Latitude"] == 0.0
        ):
            store["dic"]["Geospatial"]["Latitude"] = store["parsed"]["lat"]
            store["dic"]["Geospatial"]["Longitude"] = store["parsed"]["long"]

        yield store
    logzilla.info(f"Finished Grabbing data!")  # noqa


def nice_url(x):
    try:
        x = x.split("locations/outpatient")[1]
    except Exception:
        x = x
    return "https://www.novacare.com/contact/find-a-location" + x


def scrape():
    url = "https://novacare.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url + "/"),
        page_url=MappingField(mapping=["dic", "Url"], value_transform=nice_url),
        location_name=MappingField(
            mapping=["parsed", "name"],
            is_required=False,
        ),
        latitude=MappingField(
            mapping=["dic", "Geospatial", "Latitude"],
            value_transform=lambda x: "<MISSING>" if x == "0" or x == "0.0" else x,
            is_required=False,
        ),
        longitude=MappingField(
            mapping=["dic", "Geospatial", "Longitude"],
            value_transform=lambda x: "<MISSING>" if x == "0" or x == "0.0" else x,
            is_required=False,
        ),
        street_address=MappingField(
            mapping=["parsed", "address"],
            part_of_record_identity=True,
            is_required=False,
        ),
        city=MappingField(
            mapping=["parsed", "city"],
            is_required=False,
        ),
        state=MappingField(
            mapping=["parsed", "state"],
            is_required=False,
        ),
        zipcode=MappingField(
            mapping=["parsed", "zip"],
            is_required=False,
        ),
        country_code=MissingField(),
        phone=MappingField(
            mapping=["parsed", "phone"],
            is_required=False,
        ),
        store_number=MappingField(
            mapping=["dic", "Id"],
            part_of_record_identity=True,
            is_required=False,
        ),
        hours_of_operation=MappingField(
            mapping=["parsed", "hours"],
            is_required=False,
        ),
        location_type=MappingField(
            mapping=["parsed", "type"],
            is_required=False,
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="novacare.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
