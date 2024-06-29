
    // date selection, prevent selecting date older than today
  function getTodayDate(){
    const today = new Date();
    const yyyy=today.getFullYear();
    let mm =today.getMonth()+1;
    let dd =today.getDate();

    if (dd <10) dd = '0' + dd;
    if (mm <10) mm = '0' + mm;

    return `${yyyy}-${mm}-${dd}`
  }
  document.getElementById('dateinput').setAttribute('min',getTodayDate());
  
  const formBtn = document.getElementById('formbtn')


  formBtn.addEventListener("click", ()=>{
    let token = localStorage.getItem("token");
    if (token){
      const dateInput =document.getElementById('dateinput').value;
      const selectedTime = document.querySelector('input[name="time"]:checked').value;
      const path = window.location.pathname;
      const attractId=path.split('/')[2];
      let fee=""

      if (selectedTime=="morning"){
        fee=2000;
      } else{
        fee=2500;
      }
      // console.log(dateInput, selectedTime, fee,attractId)

      fetch("/api/booking",{
        method:"POST",
        headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        attractionId:attractId,
        date:dateInput,
        time:selectedTime,
        price:fee,

      }),
      })
      .then((resp) =>{
        return resp.json().then((data) => {
          if (!resp.ok) {
            throw new Error(`HTTP error! status: ${resp.status}, message: ${data.message}`);
          }
          return data;
        });
      })
      .then((data) => {
        if (data.ok) {
          console.log("Added successfully!");
          window.location.href='/booking'
        } else {
          console.log(data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error); 
      });  

      }else{
        signinDialog.showModal()

      }
  
  })
//wo shi fen ge xian

function setMorning() {
    document.getElementById("fee").innerText = "導覽費用： 2000元"
}
function setAfternoon() {
    document.getElementById("fee").innerText = "導覽費用： 2500元"
}

path = window.location.pathname;
// console.log(url);

function getData() { 

    let formTitle = document.querySelector(".form-title");
    let catText = document.querySelector(".cat-mrt");
    let descriptionText = document.querySelector(".description");
    let addressText = document.querySelector(".address-d");
    let transportationText = document.querySelector(".transportation-d");
    let galleryWrap = document.querySelector(".gallery-wrap");
    let dotsWrap = document.querySelector(".dots-wrap");
    let galleryFormWrap= document.querySelector(".gallery-form-wrap");
    let detailWrap=document.querySelector(".detail-wrap")
    let url = "/api" + path
    // console.log(url)

    fetch(url)
        .then((response) => {
            if(!response.ok){
                return response.json().then((error) => {
                    throw new Error(error.message);
                });
                
            }
            return response.json();

        })
        .then((data) => {
            let result = data.data;
            let name = result.name;
            let category = result.category;
            let description = result.description;
            let mrt = result.mrt;
            let address = result.address;
            let transport = result.transport;
            let images = result.images;
            


            descriptionText.innerText = description;
            addressText.innerText = address
            transportationText.innerText = transport;
            formTitle.innerText = name;
            catText.innerText = category + " at " + mrt;
            for (let i = 0; i < images.length; i++) {
                const img = document.createElement('img');
                img.classList.add("gallery");
                img.src = images[i];
                img.style.width = "540px";
                img.style.height = "400px"
                if (i == 0) {
                    img.style.display = "block";
                } else {
                    img.style.display = "none";
                }
                galleryWrap.appendChild(img);
            }
            for (let i = 0; i < images.length; i++) {
                const dot = document.createElement('span');
                dot.classList.add("dot");
                dot.addEventListener('click', function () {
                    currentSlide(i + 1); // Call the function currentSlide with parameter 1
                });
                dotsWrap.appendChild(dot);
            }
            // slideIndex = 1;
            showSlides(slideIndex);
        })
        .catch((error) => {
            galleryFormWrap.innerHTML="";
            detailWrap.innerHTML="";
            const errorMessage = document.createElement('div');
            errorMessage.innerText = "Error: " + error.message;
            galleryFormWrap.appendChild(errorMessage);
            
           
        });
}

let slideIndex = 1;
getData();


// showSlides(slideIndex);

function plusSlides(n) {
    showSlides(slideIndex += n);
}

function currentSlide(n) {
    showSlides(slideIndex = n);
}
function showSlides(n) {
    let i;
    let slides = document.getElementsByClassName("gallery");
    let dots = document.getElementsByClassName("dot");
    if (n > slides.length) { 
        slideIndex = 1;
     }
    if (n < 1) { 
        slideIndex = slides.length;
     }
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex - 1].style.display = "block";
    dots[slideIndex - 1].className += " active";
}
