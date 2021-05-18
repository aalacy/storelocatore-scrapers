from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def _valid(val):
    return val.replace("\ufeff", "").strip()


def fetch_data():
    with SgChrome() as driver:
        locator_domain = "https://www.dicarlospizza.com/"
        base_url = "https://www.dicarlospizza.com/locations"
        driver.get(base_url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//html/body/div/div[1]/div[1]/div/div[1]/div[2]",
                )
            )
        )
        locations = json.loads(
            driver.page_source.split("window.__BOOTSTRAP_STATE__ = ")[1]
            .strip()
            .split("</script>")[0]
            .strip()[:-1]
        )
        for cell in locations["siteData"]["page"]["properties"]["contentAreas"][
            "userContent"
        ]["content"]["cells"]:
            location_name = ""
            street_address = ""
            phone = ""
            coord = ["", ""]
            state = cell["content"]["elements"][1]["properties"]["title"]["quill"][
                "ops"
            ][0]["insert"].strip()
            location = cell["content"]["elements"][2]["properties"]["title"]["quill"][
                "ops"
            ]
            for x, _ in enumerate(location):
                if (
                    not _["insert"]
                    or _valid(_["insert"]) == "ORDER PICKUP"
                    or _valid(_["insert"]) == "ORDER DELIVERY"
                ):
                    continue

                if "attributes" not in _:
                    continue

                if "color" not in _["attributes"]:
                    continue

                if _["insert"] == "(" or _valid(_["insert"]) == "|":
                    continue

                if not _valid(_["insert"]):
                    continue

                if (
                    _["attributes"]["color"] == "var(--secondary-color)"
                    and "wLink" not in _["attributes"]
                    and not _["insert"][0].isdigit()
                ):
                    location_name += _valid(_["insert"])
                elif _["attributes"].get("wLink", {}).get("type", "") == "phone":
                    phone = _valid(_["insert"])
                    if not phone.startswith("("):
                        phone = "(" + phone
                elif _["attributes"].get("wLink", {}).get("type", "") == "external" or (
                    _["attributes"]["color"] == "var(--secondary-color)"
                    and _["insert"][0].isdigit()
                ):
                    street_address = _valid(_["insert"])
                    try:
                        if "wLink" in _["attributes"]:
                            map_link = _["attributes"]["wLink"]["link"]["external"]
                            coord = map_link.split("/@")[1].split("/data")[0].split(",")
                    except:
                        pass

                if location_name and street_address and phone:
                    yield SgRecord(
                        page_url=base_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=location_name,
                        state=state,
                        country_code="US",
                        phone=phone,
                        latitude=coord[0],
                        longitude=coord[1],
                        locator_domain=locator_domain,
                    )
                    location_name = street_address = phone = ""


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
