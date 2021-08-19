import csv
import sgrequests
import bs4


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    # Your scraper here
    def initSoup(link):
        return bs4.BeautifulSoup(
            sgrequests.SgRequests().get(link).text, features="lxml"
        )

    url = "https://www.mortonwilliams.com/our-locations"

    s = initSoup(url)

    locator_domain = "https://www.mortonwilliams.com/"
    missingString = "<MISSING>"

    marker = s.findAll("div", {"class": "_1lRal"})

    location_containers = [marker[0], marker[1], marker[2], marker[3], marker[4]]

    def containerGenerator(seq, sep):
        g = []
        for el in seq:
            if el == sep:
                yield g
                g = []
            g.append(el)
        yield g

    def parseContainer(c):
        container_txt = c.text
        container_list = container_txt.splitlines()
        generatedList = list(containerGenerator(container_list, u"\xa0"))
        return generatedList

    generated_containers = [
        parseContainer(location_containers[0]),
        parseContainer(location_containers[1]),
        parseContainer(location_containers[2]),
        parseContainer(location_containers[3]),
        parseContainer(location_containers[4]),
    ]

    container_list_to_json = []

    def ruleset(r):
        if len(r) == 1:
            pass
        elif len(r) == 4:
            container_list_to_json.append({"name": r[0], "phone": r[1], "hours": r[2]})
        elif len(r) == 5:
            name = r[1]
            if "Street" in r[1]:
                name = r[0] + " " + r[1]
            if "Avenue" in r[1]:
                name = r[0] + " " + r[1]
            container_list_to_json.append({"name": name, "phone": r[2], "hours": r[3]})
        elif len(r) == 6:
            name = ""
            if "Street" in r[2]:
                name = r[1] + " " + r[2]
            if "Avenue" in r[2]:
                name = r[1] + " " + r[2]
            container_list_to_json.append({"name": name, "phone": r[3], "hours": r[4]})
        else:
            new_list = []
            for e in r:
                if "Manager: Yohan1331 " in e:
                    spl_seq = e.replace("Manager: Yohan", u"\u200b").split(u"\u200b")
                    new_list.extend([spl_seq[0], spl_seq[1]])
                elif "Manager: Manny140 " in e:
                    spl_sequ = e.replace("Manager: Manny", u"\u200b").split(u"\u200b")
                    new_list.extend([spl_sequ[0], spl_sequ[1]])
                else:
                    new_list.append(e.replace(u"\u200b", ""))
            gen_l = list(containerGenerator(new_list, ""))
            for li in gen_l:
                container_list_to_json.append(
                    {
                        "name": "{} {}".format(li[1], li[2]).replace(u"\xa0", ""),
                        "phone": li[3],
                        "hours": li[4],
                    }
                )

    def parseGeneratedList(l):
        for e in l:
            for el in e:
                ruleset(el)

    parseGeneratedList(generated_containers)

    result = []

    for el in container_list_to_json:
        city = missingString
        if "Jersey City" in el["name"]:
            city = "New Jersey"
        elif "Jerome Avenue" in el["name"]:
            city = "Bronx"
        else:
            city = "Manhattan"
        result.append(
            [
                locator_domain,
                missingString,
                el["name"],
                el["name"],
                city,
                missingString,
                missingString,
                missingString,
                missingString,
                el["phone"],
                missingString,
                missingString,
                missingString,
                el["hours"],
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
