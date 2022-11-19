function myFunction() {
    var x = document.getElementById("myTopnav");
    if (x.className === "topnav") {
        x.className += " responsive";
    } else {
        x.className = "topnav";
    }
}
  
document.getElementById('logout').onclick = function logout() {
    localStorage.removeItem('C_ID');
    location.href = '/login?msg=Logged+Out';
}