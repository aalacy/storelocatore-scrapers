const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

//This table name won't change unless they overhaul their site or API calls
//given the sloppy implementation I don't expect that to be anytime soon.
//Tablename can be retrieved from the iframe element, if it needs to be reset
//then search the source of a state listing page for fusiontables.googleusercontent.com
const tableName ='1vpAly2VF-wmZjM8YJD9GD8hzZKkdkCBVu81lI-pb';

Apify.main(async () => {
  data = await axios({
    method: "GET",
    url : 'https://fusiontables.googleusercontent.com/embedviz?viz=CARD&q=select+*+from+' + tableName
  }).then((resp) => {
    returnData = [];
    dom = new JSDOM(resp.data);
    docs = dom.window.document.querySelectorAll('.googft-card-view');
    for (let d of docs){
      loc = parseCard(d.textContent);
      returnData.push({
        locator_domain: 'anixter.com',
        location_name: loc.labels,
        street_address: loc.address_line_1,
        city: loc.locality,
        state: loc.administrative_area,
        zip: loc.postal_code,
        country_code: loc.country,
        store_number: loc.store_code,
        phone: loc.primary_phone,
        location_type: '<MISSING>',
        latitude: loc.lat,
        longitude: loc.lng,
        hours_of_operation: loc.hours.join(', '),
      });
      
    }
    return returnData;
  })
  await Apify.pushData(data);
});

function parseCard(cardText){
  cardText = cardText.split(/\n/).filter((e) => {return e !== '';});
  data = {hours: []};
  for (let t of cardText){
    split = t.split(':')
    key = split.shift().toLowerCase().replace(/ |-/g, '_');
    value = split.join(':').trim();
    if (key.endsWith('hours')){
      if (value !== '' && key !== 'hours'){
        data.hours.push(key.replace('_hours', '') + " : " + value)
      }
    } else {
      if (value == '' ){value = '<MISSING>'}
      data[key] = value;
    }
  }
  return data;
}
