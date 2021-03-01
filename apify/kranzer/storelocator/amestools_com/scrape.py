import re
import base  # noqa: I900
import json
from sgrequests import SgRequests
from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("amestools_com")
session = SgRequests()


class Scrape(base.Spider):
    def crawl(self):
        base_url = "https://amestools.com/store-locator/"
        raw_json = html.fromstring(
            session.get(
                base_url,
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
                },
            ).text
        ).xpath('//script/text()[contains(., "maplistScriptParamsKo")]')[0]
        raw_json = re.findall(r"maplistScriptParamsKo = (\{.+?\});\n", raw_json)
        if raw_json:
            json_body = json.loads(raw_json[0])
            for result in json_body.get("KOObject", ["noting"])[0].get("locations", {}):
                i = base.Item(result)
                i.add_value("locator_domain", base_url)
                i.add_value("page_url", base_url)
                i.add_value(
                    "location_name", result.get("title", ""), lambda x: x.strip()
                )
                i.add_value("latitude", result.get("latitude", ""), lambda x: x.strip())
                i.add_value(
                    "longitude", result.get("longitude", ""), lambda x: x.strip()
                )
                addr = result.get("address")
                temp_phone = ""
                try:
                    temp_phone = addr.split("Phone")[1].strip()
                except:
                    pass
                addr = addr.split("Phone")[0].strip()
                addr = (
                    addr.replace("<p>", "")
                    .replace("</p>", "")
                    .strip()
                    .replace("</br>", "")
                    .replace("\n", "")
                    .strip()
                    .split("<br />")
                )
                add_list = []
                for add in addr:
                    if len("".join(add).strip()) > 0:
                        add_list.append("".join(add).strip())

                street = ""
                city = ""
                state = ""
                zip = ""
                if len(add_list) > 1:
                    street = (
                        ", ".join(add_list[:-1])
                        .strip()
                        .replace("Mission Grove Plaza,", "")
                        .strip()
                    )
                    city_state_zip = add_list[-1].strip()
                    city = city_state_zip.split(",")[0].strip()
                    state = (
                        (city_state_zip.split(",")[1].strip().split(" ", 1)[0].strip())
                        .replace(".", "")
                        .strip()
                    )
                    zip = city_state_zip.split(",")[1].strip().split(" ", 1)[-1].strip()
                elif len(add_list) == 1:
                    street = add_list[0].strip().split(",")[0].strip()
                    state_zip = add_list[0].strip().split(",")[-1].strip()
                    city = (
                        result.get("title", "")
                        .strip()
                        .split("-")[1]
                        .strip()
                        .split(":")[0]
                        .strip()
                    )
                    street = street.replace(city, "").strip()
                    state = state_zip.split(" ", 1)[0].strip().replace(".", "").strip()
                    zip = state_zip.split(" ", 1)[-1].strip()

                i.add_value("street_address", street, remove_tags, lambda x: x.strip())

                i.add_value("city", city, lambda x: x.strip())
                i.add_value("state", state, lambda x: x.strip())
                i.add_value("zip", zip, lambda x: x.strip())
                i.add_value(
                    "country_code",
                    base.get_country_by_code(i.as_dict()["state"]),
                    lambda x: x.strip(),
                )

                sub_html = html.fromstring(result["description"])
                phone = sub_html.xpath('//div[span[contains(text(), "Phone:")]]/text()')
                if len(phone) > 0:
                    i.add_value(
                        "phone",
                        sub_html.xpath(
                            '//div[span[contains(text(), "Phone:")]]/text()'
                        ),
                        base.get_first,
                        lambda x: x.strip(),
                    )
                else:
                    i.add_value(
                        "phone",
                        temp_phone.replace(":", "").replace("</p>", "").strip(),
                        lambda x: x.strip(),
                    )
                i.add_value(
                    "location_type",
                    result.get("categories", [])[0],
                    lambda x: x["title"],
                    lambda x: x.strip(),
                )
                hours = result["description"].split(
                    "<p><strong>Store Hours:</strong></p>"
                )
                if len(hours) > 1:
                    text = [
                        remove_tags(s).replace("\xa0", " ")
                        for s in hours[1].split("\n")
                        if s
                    ]
                    i.add_value(
                        "hours_of_operation", "; ".join(text), lambda x: x.strip()
                    )

                yield i


if __name__ == "__main__":
    s = Scrape()
    s.run()
