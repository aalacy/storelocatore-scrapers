const Apify = require('apify');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const axios = require('axios');
const striptags = require('striptags');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

    return await axios({
      method: 'GET',
      url: 'http://dionsbest.com/Locations.html'
    }).then((resp) => {
      dom = new JSDOM(resp.data);
      document = dom.window.document;
      rows = document.querySelectorAll('#e0 > table > tbody > tr > td > table > tbody > tr');
      addressFirst = true;
      returnData = [];
      for (let row of rows){
        sanitizedRows = sanitize(row);
        data = extract(sanitizedRows, addressFirst)
        addressFirst = addressFirst ? false : true; // Site layout switches address from first to last entry every row
        if (data !== false){
          returnData.push(data);
        }
      }
      return returnData;
    })
}

function sanitize(textRow){
  return striptags(textRow.innerHTML, '<br>')
    .replace(/(<br>){2,10}/g, "")
    .replace(/<br.*?>/g, "\n")
    .replace(/\n\n/g, "\n~\n")
    .replace(/&.*?;/g, '')
    .replace(/.*tableWorkaround.*\n/g, '')
    .replace(/^\s*\n/g, '')
    .trim()
    .replace(/~\s*~/g, '')
    .split("~")
    .filter((e) => {return e !== ''})
}

function extract(row, addressFirst){
  if (row[3] !== undefined){return false;} //Additional row holds a message about store not being open

  //Handle switching of hours/location info in site design
  addressMap = addressFirst ? splitAndFilter(row[0]) : splitAndFilter(row[2]);
  hoursMap = addressFirst? splitAndFilter(row[2]) : splitAndFilter(row[0]);
  typeMap = splitAndFilter(row[1]);

  //Pull from the arrays
  phone = addressMap.pop();
  address = addressMap.join(" ");
  city = hoursMap.shift();
  hours = hoursMap.join(" ");

  // console.log(addressMap)
  // console.log(typeMap)
  // console.log(hoursMap)
  // console.log('!@#$%^&^%$#@#$%^&*&^%$#@#$%^&*&^%$#@');

  return {
    locator_domain: 'dionsbest.com',
    location_name: '<MISSING>',
    street_address: address,
    city: city,
    state: 'FL',
    zip: '<MISSING>',
    country_code: 'US',
    store_number: '<MISSING>',
    phone: phone,
    location_type: typeMap.join(", "),
    latitude: '<MISSING>',
    longitude: '<MISSING>',
    hours_of_operation: hours
  }

}


function splitAndFilter(text){
  return text.split("\n").filter((e) => {return e !== ''})
}