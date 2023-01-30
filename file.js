const sidebar = document.getElementById("sidebar");
const hideButton = document.getElementById("hide-sidebar-button");
const showButton = document.getElementById("show-sidebar-button");

hideButton.addEventListener("click", function() {
    sidebar.classList.add("hidden");
});

showButton.addEventListener("click", function() {
    sidebar.classList.remove("hidden");
});

// Get the sidebar element
//var sidebar = document.getElementById("sidebar");

// Get the button that opens the sidebar
//var btn = document.getElementById("open-sidebar-btn");

// Add an event listener to the button that toggles the visibility of the sidebar
//btn.addEventListener("click", function() {
  //if (sidebar.style.display === "block") {
    //sidebar.style.display = "none";
  //} else {
    //sidebar.style.display = "block";
  //}
//});