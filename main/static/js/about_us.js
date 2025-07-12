window.addEventListener("scroll", () => {
  const section = document.querySelector(".about-mission");
  const overlay = document.querySelector(".mission-overlay");
  const content = document.querySelector(".mission-content");

  const scrollY = window.scrollY;
  const offset = section.offsetTop;
  const height = section.offsetHeight;

  if (scrollY > offset - height / 2 && scrollY < offset + height) {
    const progress = (scrollY - offset + height) / height;
    overlay.style.background = `rgba(255, 255, 255, ${Math.min(progress, 0.95)})`;
    content.style.transform = `translateY(${progress * -20}px)`;
    content.style.opacity = `${1 - progress * 0.3}`;
  }
});

window.addEventListener('load', () => {
  const quote = document.querySelector('.mission-quote');
  setTimeout(() => {
    quote.classList.add('visible');
  }, 800); // Delay in ms before fade-in
});