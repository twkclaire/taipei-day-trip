const signin = document.getElementById("signinItem");
const signinDialog = document.getElementById("signind");
const signinclose = document.getElementById("signinclose");
const signup = document.getElementById("signupItem");
const signupDialog = document.getElementById("signupd");
const signupclose = document.getElementById("signupclose");
const signout = document.getElementById("signoutItem");

//user sign up path
function deleteToken() {
  let token = localStorage.removeItem("token");
  // console.log("user signed out");
  window.location.reload();
  return token;
}


window.onload = function checkSigninStatus() {
  let token = localStorage.getItem("token");
  // console.log("Access token:", token);
  if (token) {
    fetch("/api/user/auth", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((resp) => {
        return resp.json().then((data) => {
          if (!resp.ok) {
            throw new Error(
              `HTTP error! status: ${resp.status}, message: ${data.message}`
            );
          }
          return data;
        });
      })
      .then((data) => {
        // console.log("Fetch successful:", data);
        signin.classList.add("hidden");
        signup.classList.add("hidden"); //Show signout only
        signout.classList.remove("hidden")

      })
      .catch((err) => {
        // console.error("Error:", err);
        signin.classList.remove("hidden");
        signup.classList.remove("hidden");
        signout.classList.add("hidden")
      });
  } else {
    // console.error("Token not found");
    signin.classList.remove("hidden");
    signup.classList.remove("hidden");
    signout.classList.add("hidden")
    
  }
}

function userSignIn(event) {
  event.preventDefault();

  var emailSign = document.getElementById("email").value;
  var passwordSign = document.getElementById("password").value;
  var signInResult=document.getElementById("resultsign");

  const authUrl = "/api/user/auth";
  fetch(authUrl, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: emailSign,
      password: passwordSign,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.token) {
        let JWTtoken = data.token;
        // console.log(JWTtoken);
        localStorage.setItem("token", JWTtoken);
        signInResult.innerText = "登入成功！！";
        window.location.reload();
      } else {
        // console.log(data.message);
        signInResult.innerText=data.message;

      }
    })
    .catch((err) => {
      console.error("Error:", err);
    });
}

//user register path
function registerUser(event) {
  event.preventDefault(); // Prevent form submission

  var nameRe = document.getElementById("namere").value;
  var emailRe = document.getElementById("emailre").value;
  var passwordRe = document.getElementById("passwordre").value;
  var resultRe = document.getElementById("resultre");
  // console.log(nameRe, emailRe, passwordRe);

  const userUrl = "/api/user";
  fetch(userUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: nameRe,
      email: emailRe,
      password: passwordRe,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.ok) {
        resultRe.innerText = "註冊成功！！";
      } else {
        resultRe.innerText = data.message;
      }
    })
    .catch((err) => {
      console.error("Error:", err); //this error handling isn't throwing my network error correctly
    });
}

//LOG IN FORM


signin.addEventListener("click", () => signinDialog.showModal());
signinclose.addEventListener("click", () => signinDialog.close());

//SIGN UP FORM


signup.addEventListener("click", () => signupDialog.showModal());
signupclose.addEventListener("click", () => signupDialog.close());

//click signIn on sign up form
function signIn() {
  signupDialog.close();
  signinDialog.showModal();
}

//click sign up on Sign in form

function signUp() {
  signupDialog.showModal();
  signinDialog.close();
}
