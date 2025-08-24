let current = 0;
const images = document.querySelectorAll('.farmer-image');

setInterval(() => {
  images[current].classList.remove('active');
  current = (current + 1) % images.length;
  images[current].classList.add('active');
}, 4000); // change image every 4 seconds
