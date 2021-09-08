from sgrequests import SgRequests
import json

def extract_json(html_string):
    html_string = (
        html_string.replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .replace(" /* forcing open state for all FCs*/", "")
    )
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects

session = SgRequests()
search_code = "35208"

url = (
    "https://www.regions.com/Locator?regions-get-directions-starting-coords=&daddr=&autocompleteAddLat=&autocompleteAddLng=&r=&geoLocation="
    + search_code
    + "&type=branch"
)

response = session.get(url).text
first_objects = extract_json(response)

with open("file.txt", "w", encoding="utf-8") as output:
    print(response, file=output)

with open("json.txt", "w", encoding="utf-8") as output:
    json.dump(first_objects, output, indent=4)