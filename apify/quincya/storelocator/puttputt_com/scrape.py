import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("puttputt_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://puttputt.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    all_links = []
    final_links = []

    items = base.find(class_="entry-content").find_all("a")
    for item in items:
        link = item["href"]
        if link not in all_links:
            all_links.append(link)

    for link in all_links:
        if "locations" not in link:
            final_links.append([link, "", "", "", ""])
        else:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            items = base.find(id="content").find_all("p")
            for item in items:
                try:
                    street = item.find(class_="mini_body").text.split("\n")[-2]
                    city_state = item.strong.text.replace("Putt-Putt", "").strip()
                    phone = item.find(class_="mini_body").text.split("\n")[-1]
                    fin_link = item.a["href"]
                    final_links.append([fin_link, street, city_state, phone, link])
                except:
                    pass

    for final_link in final_links:

        locator_domain = "puttputt.com"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        if "www.puttputtfunhouse.com" in final_link[0]:
            continue

        link = final_link[0]
        street_address = final_link[1]
        try:
            city = final_link[2].split(",")[0].strip()
            state = final_link[2].split(",")[1].strip()
        except:
            pass
        location_name = "Putt-Putt Fun Center"
        phone = final_link[3]
        zip_code = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        if "funworks" in final_link[0]:
            link = "https://funworksfuncompany.com/directions-hours"
            phone_link = "https://funworksfuncompany.com/contact-us-2"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            location_name = base.h1.strong.text
            street_address = str(base.h1).split("<br/>")[-2]
            city_line = (
                str(base.h1).split("<br/>")[-1].replace("</h1>", "").strip().split(",")
            )
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            phone_link = "https://funworksfuncompany.com/contact-us-2"
            req = session.get(phone_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                phone = re.findall(
                    r"[(\d)]{3}-[\d]{3}-[\d]{4}", base.find(class_="content").text
                )[0]
            except:
                phone = "<MISSING>"

            hours_of_operation = ""
            ps = base.find_all("p")
            for p in ps:
                if "day" in p.text.lower() and "Re-Opening" not in p.text:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + p.text.replace("\n", " ").replace("!", " ").replace("–", "-")
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

            latitude = "<MISSING>"
            longitude = "<MISSING>"

        elif "hope-mills" in final_link[0]:
            link = "https://puttputt.com/hope-mills/plan/"
            if "3311 Footbridge" in street_address:
                zip_code = "28306"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = ""
            ps = base.find_all("p")
            for p in ps:
                if "day" in p.text.lower() or "spring break" in p.text.lower():
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + p.text.replace("\n", " ").replace("!", " ").replace("–", "-")
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        elif "farragutputtputt" in final_link[0]:
            if "164 West" in street_address:
                zip_code = "37934"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = ""
            ps = base.find_all(style="color:#FFFFFF")
            for p in ps:
                if "day" in p.text.lower() or "0p" in p.text.lower():
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + p.text.replace("\n", " ")
                        .replace("\xa0", "")
                        .replace("–", "-")
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        elif "cedarcreeksportscenter" in final_link[0]:
            if "10770 Lebanon" in street_address:
                zip_code = "37122"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = ""
            ps = base.find_all(class_="size20 ArialNarrow20")
            for p in ps:
                if "day" in p.text.lower() or "0p" in p.text.lower():
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + p.text.replace("\n", " ")
                        .replace("Â\xa0", "")
                        .replace("–", "-")
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        elif "golfandgamesmemphis" in final_link[0]:
            if "5484 Summer" in street_address:
                zip_code = "38134"
                latitude = "35.16191"
                longitude = "-89.87715"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = ""
            ps = base.find(class_="entry-content").find_all("strong")
            for p in ps:
                if (
                    "day" in p.text.lower()
                    or "a.m" in p.text.lower()
                    or "p.m" in p.text.lower()
                ):
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + p.text.replace("\n", " ").replace("–", "-")
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        elif "fortwayneputtputt" in final_link[0]:
            if "4530 Speedway" in street_address:
                zip_code = "46825"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = (
                " ".join(list(base.find(id="iecwtabe").stripped_strings))
                .replace("\xa0", "")
                .replace("\u200b", "")
                .replace("Hours of operation:", "")
                .strip()
            )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        elif "puttlongview" in final_link[0]:
            if "2630 Bill Owens" in street_address:
                zip_code = "75604"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = ""
            ps = base.find(id="zC").find_all("p")
            for p in ps:
                if "day" in p.text.lower() or "pm" in p.text.lower():
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + p.text.replace("Â", " ").replace("\xa0", "")
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        elif "puttputtofwarren.com" in final_link[0]:
            if "3937 Youngstown" in street_address:
                zip_code = "44484"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = base.find(id="hours").text.replace("\n", " ").strip()
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        elif ".myputtputt.com" in final_link[0]:
            link = "https://www.myputtputt.com/public/contact_us/hours.cfm"
            if "7901 Midlothian" in street_address:
                zip_code = "23235"
                latitude = "37.499972"
                longitude = "-77.542233"
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = ""
            ps = base.find(id="body_copy").find_all("p")
            for p in ps:
                if "day" in p.text.lower() or "hours" in p.text.lower():
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + p.text.replace("\n", " ").replace("\xa0", "")
                    )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        elif (
            "/puttputt.com/" not in final_link[0]
            and ".puttputt.com" not in final_link[0]
            and "puttputtpa" not in final_link[0]
        ):
            zip_code = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            link = final_link[-1]

        else:
            if "puttputtpa.com" in final_link[0]:
                link = "http://www.puttputtpa.com/mini_about.html"
            elif "lynchburg" in final_link[0]:
                link = (final_link[0] + "hours-location").replace(
                    "burghours", "burg/hours"
                )
            else:
                link = final_link[0] + "hoursinfo"

            logger.info(link)

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            raw_address = ""
            minis = base.find_all(class_="mini_body")
            for mini in minis:
                if (
                    "putt-putt" in mini.text.lower()
                    and "bumper" not in mini.text.lower()
                ):
                    raw_address = mini.text.split("\n")
                    break
            if not raw_address:
                minis = base.find_all("p")
                for mini in minis:
                    if (
                        "putt-putt" in mini.text.lower()
                        and "bumper" not in mini.text.lower()
                    ):
                        raw_address = mini.text.split("\n")
                        break

            if raw_address:
                location_name = raw_address[0].strip()
                street_address = raw_address[-3].strip()
                city_line = raw_address[-2].strip().split(",")
                if "fun center" in street_address.lower():
                    street_address = raw_address[-2].strip()
                    city_line = raw_address[-1].strip().split(",")
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
            else:
                if link == "https://puttputt.com/hope-mills/hoursinfo":
                    location_name = "Putt-Putt Hope Mills"
                    street_address = "3311 Footbridge Ln."
                    city = "Fayetteville"
                    state = "NC"
                    phone = "910-424-7888"
                    data.append(
                        [
                            locator_domain,
                            link,
                            location_name,
                            street_address,
                            city,
                            state,
                            "<MISSING>",
                            country_code,
                            "<MISSING>",
                            phone,
                            "<MISSING>",
                            "<MISSING>",
                            "<MISSING>",
                            "<MISSING>",
                        ]
                    )
                    continue
                else:
                    logger.info("No data found")
                    break

            try:
                phone = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", str(base))[0]
            except:
                try:
                    phone = re.findall(r"[(\d)]{3}\.[\d]{3}\.[\d]{4}", str(base))[0]
                except:
                    phone = "<MISSING>"
            if link == "https://puttputt.com/charlottesville/hoursinfo":
                phone = "(434) 973-5509"
            if link == "https://puttputt.com/amelia-island/hoursinfo":
                phone = "904-261-4443"
            hours_of_operation = ""
            try:
                ps = base.find(id="content").find_all("p")
                if "pm" not in str(ps).lower():
                    ps = base.find(id="content").find_all("h4")
            except:
                ps = base.find_all("tr")[1:]
            for p in ps:
                if "pm" in p.text.lower() or "am –" in p.text.lower():
                    if (
                        "March – October" in p.text
                        or "THANKSGIVING" in p.text
                        or "HOURS BEGINNING" in p.text
                    ):
                        break
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + p.text.replace("\n", " ").replace("!", " ").replace("–", "-")
                    )
            if hours_of_operation.count("Monday") > 1:
                hours_of_operation = hours_of_operation[
                    : hours_of_operation.rfind("Monday")
                ].strip()
            if hours_of_operation.count("Sunday") > 1:
                hours_of_operation = hours_of_operation[
                    : hours_of_operation.rfind("Sunday")
                ].strip()
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
            if "*" in hours_of_operation:
                hours_of_operation = hours_of_operation[
                    : hours_of_operation.find("*")
                ].strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            try:
                map_link = base.find("a", attrs={"target": "_blank"})["href"]
                at_pos = map_link.rfind("@")
                latitude = map_link[at_pos + 1 : map_link.find(",", at_pos)].strip()
                longitude = map_link[
                    map_link.find(",", at_pos) + 1 : map_link.find(",", at_pos + 15)
                ].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            if "1080 North Marr Rd" in street_address:
                latitude = "39.209968"
                longitude = "-85.885098"
            elif "3311 Footbridge Lane" in street_address:
                latitude = "34.981662"
                longitude = "-78.97214"
            elif "8105 Timberlake Road" in street_address:
                latitude = "37.350075"
                longitude = "-79.231941"
            elif len(latitude) > 15:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            elif "puttputtpa.com" in link:
                latitude = "39.92672"
                longitude = "-75.304327"

        if "6801 Peters" in street_address:
            zip_code = "24019"

        if not hours_of_operation:
            hours_of_operation = "MISSING"

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state.split("(")[0].strip(),
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
