let slideIndex = 0;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;

function showSlides() {
    slides.forEach((slide) => {
        slide.style.transform = `translateX(-${slideIndex * 100}%)`;
    });
}

function moveSlide(n) {
    slideIndex = (slideIndex + n + totalSlides) % totalSlides;
    showSlides();
}

let slideInterval = setInterval(() => {
    moveSlide(1);
}, 5000);

showSlides();

function adjustFooterPosition() {
    const body = document.body;
    const html = document.documentElement;
    const windowHeight = window.innerHeight;
    const bodyHeight = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
    const footer = document.querySelector('footer');
    if (windowHeight >= bodyHeight) {
        // If window height is greater than or equal to body height, position footer at the bottom of the viewport
        footer.style.position = 'fixed';
        footer.style.bottom = '0';
    } else {
        // If body height is greater than window height, position footer at the bottom of the content
        footer.style.position = 'static';
    }
}

window.addEventListener('load', adjustFooterPosition);
window.addEventListener('resize', adjustFooterPosition);