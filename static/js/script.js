// Реальные фото портфолио (последние загруженные), отдаются сервером
// через <script id="hero-slides-data" type="application/json"> - см. index.html.
const slidesData = JSON.parse(document.getElementById('hero-slides-data')?.textContent || '[]');

const slidesRoot = document.getElementById('slides');
const dotsRoot = document.getElementById('dots');
const heroCopy = document.getElementById('heroCopy');

// Рендер фоновых изображений + точки
slidesData.forEach((s, i) => {
  const el = document.createElement('div');
  el.className = 'slide' + (i === 0 ? ' is-active' : '');
  const img = document.createElement('img');
  img.src = s.image;
  img.alt = s.title;
  img.className = 'bg';
  el.appendChild(img);
  slidesRoot.appendChild(el);

  const dot = document.createElement('button');
  dot.className = 'dot' + (i === 0 ? ' is-active' : '');
  dot.setAttribute('role','tab');
  dot.setAttribute('aria-label', `Слайд ${i+1}`);
  dot.addEventListener('click', () => goTo(i, true));
  dotsRoot.appendChild(dot);
});

function setCopy(i){
  if (slidesData.length === 0) {
    heroCopy.innerHTML = `
      <h1 class="step-in delay-1">Кованые решётки, ворота, навесы и перила</h1>
      <p class="step-in delay-2">Изготовление и монтаж металлоконструкций в Ташкенте под ключ.</p>
      <div class="hero-cta step-in delay-3"><a class="btn" href="/projects/">Смотреть</a></div>`;
    return;
  }
  const total = String(slidesData.length).padStart(2,'0');
  const current = String(i+1).padStart(2,'0');
  heroCopy.innerHTML = `
    <div class="kicker step-in">${current} / ${total}</div>
    <h1 class="step-in delay-1">${slidesData[i].title}</h1>
    <p class="step-in delay-2">${slidesData[i].text}</p>
    <div class="hero-cta step-in delay-3">
      <a class="btn" href="/projects/">Смотреть</a>
    </div>`;
}


let index = 0, timer = null, hovering = false, blocked = false;
const slideEls = [...document.querySelectorAll('.slide')];
const dotEls = [...document.querySelectorAll('.dot')];
setCopy(0);

function goTo(i, user=false){
  if(slideEls.length === 0 || blocked || i === index) return;
  blocked = true;
  slideEls[index].classList.remove('is-active');
  dotEls[index].classList.remove('is-active');
  index = (i + slideEls.length) % slideEls.length;
  slideEls[index].classList.add('is-active');
  dotEls[index].classList.add('is-active');
  setCopy(index);
  setTimeout(()=> blocked = false, 820);
  if(user) restart();
}

function next(){ goTo(index+1); }

function start(){ timer = setInterval(()=>{ if(!hovering && !document.hidden) next(); }, 5000); }
function stop(){ clearInterval(timer); timer=null; }
function restart(){ stop(); start(); }

// Пауза при наведении и на сворачивание вкладки
document.querySelector('.hero').addEventListener('mouseenter', ()=> hovering=true);
document.querySelector('.hero').addEventListener('mouseleave', ()=> hovering=false);
document.addEventListener('visibilitychange', ()=> { if(document.hidden) stop(); else start(); });

// Стрелки ← →
document.addEventListener('keydown', (e)=>{
  if(e.key === 'ArrowRight') { goTo(index+1,true); }
  if(e.key === 'ArrowLeft')  { goTo(index-1,true); }
});

// Хедер — меняем фон при скролле
const header = document.getElementById('header');
const onScroll = ()=> header.classList.toggle('scrolled', window.scrollY > 4);
onScroll();
window.addEventListener('scroll', onScroll, {passive:true});

// Scroll-reveal
const io = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      e.target.classList.add('is-visible');
      io.unobserve(e.target);
    }
  })
},{threshold:0.08});
document.querySelectorAll('[data-reveal]').forEach(el=> io.observe(el));

// Подключаем карточки портфолио к reveal
document.querySelectorAll('#portfolioGrid .card').forEach(el=> {
  if (typeof io !== 'undefined') io.observe(el);
});

// ====== Маска телефона (простая, без зависимостей)
(function phoneMask(){
  const input = document.getElementById('phone');
  if(!input) return;
  const template = '+998 (__) ___-__-__';
  const digits = () => input.value.replace(/\D/g,'').slice(0,12); // +998 + 9 цифр -> итого 12 символов включая 998
  function format(){
    let d = digits();
    if(d.startsWith('998')) d = d; else if(d.startsWith('8')) d = '998' + d.slice(1);
    else if(d.length && !d.startsWith('998')) d = '998' + d;
    let res = '+998 (';
    const body = d.slice(3); // после кода страны
    const parts = [body.slice(0,2), body.slice(2,5), body.slice(5,7), body.slice(7,9)];
    res += (parts[0]||'__') + ') ' + (parts[1]||'___') + '-' + (parts[2]||'__') + '-' + (parts[3]||'__');
    input.value = res;
  }
  input.addEventListener('input', format);
  input.addEventListener('focus', ()=>{ if(!input.value) input.value = template; });
  input.addEventListener('blur', ()=>{
    // если мало цифр — очищаем
    const count = input.value.replace(/\D/g,'').length;
    if(count < 12) input.value = '';
  });
})();

// Отправка формы заявки идёт обычным POST на сервер (Django views.home) -
// на клиенте оставлена только маска телефона (phoneMask выше), без
// перехвата submit, чтобы данные реально доходили до бэкенда.

// Автозапуск
start();
// ====== Mobile burger menu (dropdown under header)
document.addEventListener('DOMContentLoaded', function() {
            const menu = document.getElementById('mobileNav');
            const burger = document.querySelector('.burger');
            
            if (!menu || !burger) {
                console.log('Elements not found');
                return;
            }

            let isOpen = false;

            function openMenu() {
                if (isOpen) return;
                isOpen = true;
                
                // Показываем меню и получаем его высоту
                menu.style.display = 'block';
                const target = menu.scrollHeight;
                
                // Начинаем с высоты 0
                menu.style.height = '0px';
                menu.style.transition = 'height 0.28s ease';
                
                // Анимируем до полной высоты
                requestAnimationFrame(() => {
                    menu.style.height = target + 'px';
                });
                
                burger.setAttribute('aria-expanded', 'true');
                document.body.classList.add('menu-open');
                console.log('Menu opened');
            }

            function closeMenu() {
                if (!isOpen) return;
                isOpen = false;
                
                // Получаем текущую высоту и анимируем к 0
                const current = menu.scrollHeight;
                menu.style.height = current + 'px';
                menu.style.overflow = 'hidden';
                menu.style.transition = 'height 0.28s ease';
                
                requestAnimationFrame(() => {
                    menu.style.height = '0px';
                });

                // После завершения анимации скрываем меню
                const onTransitionEnd = (e) => {
                    if (e.propertyName !== 'height') return;
                    menu.removeEventListener('transitionend', onTransitionEnd);
                    
                    menu.style.display = 'none';
                    menu.style.height = '';
                    menu.style.transition = '';
                    menu.style.overflow = '';
                };
                
                menu.addEventListener('transitionend', onTransitionEnd);
                
                // Fallback timeout на случай проблем с transitionend
                setTimeout(() => {
                    if (!isOpen) {
                        menu.style.display = 'none';
                        menu.style.height = '';
                        menu.style.transition = '';
                        menu.style.overflow = '';
                    }
                }, 300);
                
                burger.setAttribute('aria-expanded', 'false');
                document.body.classList.remove('menu-open');
                console.log('Menu closed');
            }

            function toggleMenu() {
                console.log('Toggle clicked, isOpen:', isOpen);
                if (isOpen) {
                    closeMenu();
                } else {
                    openMenu();
                }
            }

            // События
            burger.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleMenu();
            });

            // Закрытие по ESC
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && isOpen) {
                    closeMenu();
                }
            });

            // Закрытие при клике на ссылки в меню
            menu.addEventListener('click', function(e) {
                if (e.target.tagName === 'A' && isOpen) {
                    closeMenu();
                }
            });

            // Закрытие при изменении размера экрана на десктоп
            const mediaQuery = window.matchMedia('(min-width: 900px)');
            mediaQuery.addEventListener('change', function(e) {
                if (e.matches && isOpen) {
                    closeMenu();
                }
            });

            // Инициализация
            burger.setAttribute('aria-expanded', 'false');
            menu.style.display = 'none';
            
            console.log('Mobile menu script loaded');
        });