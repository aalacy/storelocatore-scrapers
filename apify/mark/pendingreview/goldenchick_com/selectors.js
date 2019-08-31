const locationNameSelector = 'meta[property="og:title"]';
const streetAddressSelector = 'meta[property="business:contact_data:street_address"]';
const citySelector = 'meta[property="business:contact_data:locality"]';
const stateSelector = 'meta[property="business:contact_data:region"]';
const zipSelector = 'meta[property="business:contact_data:postal_code"]';
const countrySelector = 'meta[property="business:contact_data:country_name"]';
const phoneSelector = 'meta[property="business:contact_data:phone_number"]';
const latitudeSelector = 'meta[property="place:location:latitude"]';
const longitudeSelector = 'meta[property="place:location:longitude"]';
const hoursSelector = '#col_one';

module.exports = {
  locationNameSelector,
  streetAddressSelector,
  citySelector,
  stateSelector,
  zipSelector,
  countrySelector,
  phoneSelector,
  latitudeSelector,
  longitudeSelector,
  hoursSelector,
};
