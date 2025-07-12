let currentSlide = 0;
const slidesWrapper = document.getElementById("slidesWrapper");
const totalSlides = document.querySelectorAll(".slide").length;
const dotsContainer = document.getElementById("sliderDots");

// Create dots dynamically
for (let i = 0; i < totalSlides; i++) {
  const dot = document.createElement("div");
  dot.classList.add("dot");
  dot.addEventListener("click", () => {
    currentSlide = i;
    updateSlidePosition();
    updateDots();
  });
  dotsContainer.appendChild(dot);
}

const dots = document.querySelectorAll(".slider-dots .dot");

function updateSlidePosition() {
  slidesWrapper.style.transform = `translateX(-${currentSlide * 100}%)`;
  updateDots();
}

function updateDots() {
  dots.forEach((dot, index) => {
    dot.classList.toggle("active", index === currentSlide);
  });
}

function nextSlide() {
  currentSlide = (currentSlide + 1) % totalSlides;
  updateSlidePosition();
}

function prevSlide() {
  currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
  updateSlidePosition();
}

// Auto-slide every 6 seconds
setInterval(nextSlide, 6000);

// Set initial active dot
updateDots();