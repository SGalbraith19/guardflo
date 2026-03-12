document.addEventListener("DOMContentLoaded", () => {
   const fadeElements = document.querySelectorAll(".fade-in");
   fadeElements.forEach(el => {
       el.style.opacity = 0;
       el.style.transform = "translateY(20px)";
       setTimeout(() => {
           el.style.transition = "all 0.6s ease";
           el.style.opacity = 1;
           el.style.transform = "translateY(0)";
       }, 300);
   });
});

window.addEventListener("scroll", function() {

const header = document.querySelector(".site-header");

if (window.scrollY > 20) {
header.classList.add("scrolled");
} else {
header.classList.remove("scrolled");
}

});