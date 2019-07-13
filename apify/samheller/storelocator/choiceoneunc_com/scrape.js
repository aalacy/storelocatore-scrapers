const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape(){
  return await axios({
    method: 'GET',
    url: 'https://choiceoneuc.com/locations/'
  }).then((resp) => {
     dom = new JSDOM(resp.data);
     document = dom.window.document;
     rows = document.querySelectorAll('div.store')
     data = [];
     for (let row of rows){
        row = sanitize(row.textContent);
        area = parseArea(row[2]);
        phone = row[3].replace('Phone:', '').trim();
        hours = row[5].replace('Hours:', '').trim();
        data.push({
          locator_domain: 'choiceoneuc.com',
          location_name: row[0],
          street_address: row[1],
          city: area.city,
          state: area.state,
          zip: area.zip,
          country_code: 'US',
          store_number: '<MISSING>',
          phone: phone,
          location_type: '<MISSING>',
          latitude: '<MISSING>',
          longitude: '<MISSING>',
          hours_of_operation: hours,
        })
     }
     return data;
  })
}


function sanitize(textRow){
  sane = [];
  for (s of textRow.split("\n")){
    s = s.trim();
    if (s !== ''){sane.push(s);}
  }
  return sane;
}

function parseArea(area){
  parsed = {city: '', state: '', zip: ''};
  area = area.split(',');
  parsed.city = area[0];
  area = area[1].split(' ');
  parsed.zip = area.pop();
  parsed.state = area.join(' ').trim();
  return parsed;
}