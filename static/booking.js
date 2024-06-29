var main=""
var submitPrice=""
var itineraryIntro=document.getElementById('itinerary-intro');
var itineraryIntroNoBooking=document.getElementById('itinerary-intro-no-booking');
const submitText=document.getElementById('submit-text');
const bookingWrap=document.getElementById('booking-wrap');
const noBookingWrap=document.getElementById('no-booking-wrap');
const contactForm=document.getElementById('contact-form');
const icardInfo=document.getElementById('card-info');
const submitWrap=document.getElementById('submit-wrap');
const noBookingText=document.getElementById('no-booking-tex');
const danger=document.getElementById('danger');
const footer=document.getElementById('footer');

danger.addEventListener('click', () => {
  let token = localStorage.getItem("token");

  fetch("/api/booking", {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((resp) => {
      return resp.json().then((data) => {
        if (!resp.ok) {
          throw new Error(`HTTP error! status: ${resp.status}, message: ${data.message}`);
        }
        return data;
      });
    })
    .then((data) => {
      console.log(data.data)
      location.reload();
    })
    .catch((error) => {
      console.error("Error:", error);
      
    });
});

function getBooking() {
  let token = localStorage.getItem("token");

  if (token == null){
    window.location.href="/"
  }else{
    fetch("/api/booking",{
      method:"GET",
      headers:{ Authorization: `Bearer ${token}` }, 
    })
        .then((resp) => {
        return resp.json().then((data) => {
          if (!resp.ok) { 
            window.location.href="/"
            throw new Error(
              `HTTP error! status: ${resp.status}, message: ${data.message}`
            );
          }
          return data;
        });
      })
        .then((data) => {
            // console.log(data)
            
            if (!data.data){
              noBookingWrap.classList.remove('hidden-content');
              itineraryIntroNoBooking.innerHTML=`您好，${userName}，待預訂的行程如下：`;
              footer.style.height="100%";

            }else{

              bookingWrap.classList.remove('hidden-content');
              const name=data.data.attraction.name;
              const address=data.data.attraction.address;
              const time=data.data.time; 
              const date=data.data.date;
              const price=data.data.price;
              const img= data.data.attraction.image;
              if (time=='morning'){
                booktime='早上 9 點到中午 12 點'
              } else{
                booktime='中午 12 點到中午 4 點'
              }
            //   console.log(name,address, time, date, price);
              let itineraryText=document.getElementById("itinerary-text");
              let itineraryImg=document.getElementById("itinerary-img");
              itineraryImg.src=img;
              itineraryIntro.innerHTML=`您好，${userName}，待預訂的行程如下：`
              main += `
                        <p class="itinerary-title">台北一日遊：${name}</p>
                        <p><b>日期：</b>${date}</p>
                        <p><b>時間：</b>${booktime}</p> 
                        <p><b>費用：</b>新台幣${price}元</p>
                        <p><b>地點：</b>${address}</p>
                      `;
              itineraryText.innerHTML=main;
              submitPrice +=`<p>總價：新台幣${price}元<p>`;
              submitText.innerHTML=submitPrice;  


            }

        })
        .catch((error) => {
          console.error("Error:", error);
          window.location.href="/"

      });
    }
  

}
document.addEventListener('userSignedIn', getBooking);