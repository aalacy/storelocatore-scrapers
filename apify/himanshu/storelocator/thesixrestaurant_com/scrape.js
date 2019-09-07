const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
 
var url_tmp  = 'http://www.thesixrestaurant.com';
var url = 'http://www.thesixrestaurant.com/locations/';
async function scrape(){

  return new Promise(async (resolve,reject)=>{
 
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
        var items=[];
        
     
        var main = $('.container').find('.row').find('.medium-6');
        function mainhead(i)

        {
            if(main.length>i)

                {
          var link = url_tmp+$('.container').find('.row').find('.medium-6').eq(i).find('a').attr('href');

          request(link,(err,res,html)=>{

            if(!err && res.statusCode==200){
              const $  =cheerio.load(html);
              var main1 =$('.container').find('.medium-6 ').find('p').text();
              var address_tmp =main1.split('Reservation');
              var address_tmp1 = address_tmp[1].split(',');
              var tmp = $('.container').find('.row').find('p').text().split('Reservation');
              var address_tmp2 = address_tmp1[2].trim().replace('undefined25% off after 6 pmWine Wednesdays: 1/2 off selected bottlesSaturday/Sunday Brunch: 10 am to 2 pm/Bottomless till 2 pm','');
              var address_tmp3 = address_tmp2.replace('Live music and entertainment most nights!','');
              var address_tmp4 = address_tmp3.replace('Featuring: Bloody Mary Bar and Bottomless Mimosas!Best Happy Hour in Town: 7 Days a Week from 3 to 6 pm','');
              var address = address_tmp4.replace('25% off after 6 pmWine Wednesdays: 1/2 off selected bottlesSaturday/Sunday Brunch: 10 am to 2 pm/Bottomless till 2 pm','').replace(/<[^>]*>?/gm, '').trim();
              var city = address_tmp1[3].trim();
              var state_tmp = address_tmp1[4].replace('  You can now make a reservation via Yelp! <a href=https://www.yelp.com/reservations/the-six-chow-house-studio-city>Reserve at The Six Chow House on Yelp</a>','');
              var state_tmp1 = state_tmp.split(' ');
              var state = state_tmp1[1].trim();
              var zip =state_tmp1[2].trim();
              var hour = address_tmp1[0]+address_tmp1[1].trim().replace('Neighborhood Night: Mondays','');
              var phone_tmp = address_tmp1[4].split('\t\t');
              var phone_tmp1 = phone_tmp[1].split('\n');
              var phone = phone_tmp1[0];
             
              
              var location_name = $('.large-9').find('h1').text();
              items.push({  

                locator_domain: 'http://www.thesixrestaurant.com', 

                location_name: location_name, 

                street_address: address,

                city: city, 

                state: state,

                zip:  zip,

                country_code: 'US',

                store_number: '<MISSING>',

                phone: phone,

                location_type: 'thesixrestaurant',

                latitude: '<MISSING>',

                longitude: '<MISSING>', 

                hours_of_operation: hour});
                mainhead(i+1);
             

           }

          });
        }


        else{
    
        resolve(items);
    
        }
  } 
  
  mainhead(0); 
            
            }
    });
  });
}

  
    
   
  
  Apify.main(async () => {
  
      
  
      const data = await scrape();
      
      
       await Apify.pushData(data);
    
    });