// Слайды (замени картинки/тексты при необходимости)
const slidesData = [
  {
    title: "Inferno",
    text: "Погрузитесь в атмосферу современного модерна с кухней Inferно — сочетание стиля и технологий в каждой детали!",
    image: "https://images.unsplash.com/photo-1600585154526-990dced4db0d?q=80&w=1920&auto=format&fit=crop"
  },
  {
    title: "Destiny",
    text: "Откройте дверь в свой мир с кухней Destiny — современный стиль и неповторимая элегантность!",
    image: "https://images.unsplash.com/photo-1620799139507-1ff5b51c0702?q=80&w=1920&auto=format&fit=crop"
  },
  {
    title: "Glass All",
    text: "Создайте уникальное пространство с дизайнерскими гардеробными Glass All от Dall’Agnese.",
    image: "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?q=80&w=1920&auto=format&fit=crop"
  }
];

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
  const total = String(slidesData.length).padStart(2,'0');
  const current = String(i+1).padStart(2,'0');
  heroCopy.innerHTML = `
    <div class="kicker step-in">${current} / ${total}</div>
    <h1 class="step-in delay-1">${slidesData[i].title}</h1>
    <p class="step-in delay-2">${slidesData[i].text}</p>
    <div class="hero-cta step-in delay-3">
      <a class="btn" href="/catalog/">Смотреть</a>
    </div>`;
}


let index = 0, timer = null, hovering = false, blocked = false;
const slideEls = [...document.querySelectorAll('.slide')];
const dotEls = [...document.querySelectorAll('.dot')];
setCopy(0);

function goTo(i, user=false){
  if(blocked || i === index) return;
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

// === Portfolio chips filter (scoped, supports category + allow-list by IDs) ===
(function portfolioFilter(){
  const chipsWrap = document.getElementById('portfolioChips');
  const grid = document.getElementById('portfolioGrid');
  if(!chipsWrap || !grid) return;

  const chips = Array.from(chipsWrap.querySelectorAll('.chip'));
  const cards = Array.from(grid.querySelectorAll('.card'));

  // Map human labels (or data-filter) -> internal cfg
  // cat: 'all' | 'grilles' | 'gates' | 'canopy' | 'railings' | your custom keys
  // ids: optional allow-list of specific cards by id or data-id
  const FILTER_MAP = {
    'all': { cat: 'all' },
    'Смотреть все категории': { cat: 'all' },
    'Все направления': { cat: 'all' },
    'Решётки': { cat: 'grilles' },
    'Ворота': { cat: 'gates' },
    'Навесы': { cat: 'canopy' },
    'Перила': { cat: 'railings' },
    // Пример точечного выбора карточек по ID (раскомментируй и подставь свои):
    // 'Премиум решётки': { cat: 'grilles', ids: ['gr-01','gr-07','gr-12'] }
  };

  function applyFilter(key){
    const cfg = FILTER_MAP[key] || { cat: key };
    const ids = new Set((cfg.ids || []).filter(Boolean));
    let visible = 0;

    cards.forEach(card => {
      const cat = card.dataset.cat || '';
      const cardId = card.dataset.id || card.id || '';
      const catOk = cfg.cat === 'all' || cat === cfg.cat;
      const idOk = ids.size === 0 || (cardId && ids.has(cardId));
      const show = catOk && idOk;

      card.style.display = show ? '' : 'none';
      card.setAttribute('aria-hidden', show ? 'false' : 'true');
      if (show) visible++;
    });

    grid.classList.toggle('is-empty', visible === 0);
  }

  function setActive(btn){
    chips.forEach(c => {
      const isActive = c === btn;
      c.classList.toggle('active', isActive);
      c.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });
  }

  chipsWrap.addEventListener('click', (e)=>{
    const btn = e.target.closest('.chip');
    if(!btn) return;
    const key = btn.dataset.filter || btn.textContent.trim();
    setActive(btn);
    applyFilter(key);
  });

  // Initial state
  const initial = chips.find(c => c.classList.contains('active')) || chips[0];
  if(initial){
    setActive(initial);
    applyFilter(initial.dataset.filter || initial.textContent.trim());
  } else {
    applyFilter('all');
  }

  // expose API
  window.filterPortfolio = applyFilter;
})();

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

// ====== Валидация и отправка формы (демо)
(function ctaFormInit(){
  const form = document.getElementById('ctaForm');
  if(!form) return;
  const name = form.querySelector('#name');
  const phone = form.querySelector('#phone');
  const agree = form.querySelector('#agree');
  const note = form.querySelector('.form-note');

  function setError(el, msg){
    const err = el.closest('.field')?.querySelector('.error') || form.querySelector('.error:last-of-type');
    if(err) err.textContent = msg || '';
    el.setAttribute('aria-invalid', msg ? 'true' : 'false');
  }

  function validate(){
    let ok = true;
    // name
    if(!name.value.trim()){
      setError(name, 'Укажите имя');
      ok = false;
    } else setError(name, '');

    // phone (+998 и ещё 9 цифр)
    const d = phone.value.replace(/\D/g,'');
    if(d.length !== 12 || !d.startsWith('998')){
      setError(phone, 'Введите телефон в формате +998 (90) 123-45-67');
      ok = false;
    } else setError(phone, '');

    // agree
    if(!agree.checked){
      const err = form.querySelectorAll('.error')[form.querySelectorAll('.error').length-1];
      if(err) err.textContent = 'Нужно согласие на обработку данных';
      ok = false;
    } else {
      const err = form.querySelectorAll('.error')[form.querySelectorAll('.error').length-1];
      if(err) err.textContent = '';
    }
    return ok;
  }

  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    note.textContent = '';
    if(!validate()) return;

    // имитация отправки
    form.classList.add('sending');
    note.textContent = 'Отправляем...';
    try{
      await new Promise(r=> setTimeout(r, 800)); // тут вставишь свой fetch к бэкенду
      note.textContent = 'Спасибо! Мы свяжемся с вами в ближайшее время.';
      form.reset();
    }catch(err){
      note.textContent = 'Ошибка отправки. Попробуйте позже.';
    }finally{
      form.classList.remove('sending');
    }
  });
})();

// Подключаем карточки каталога к reveal (если есть io из lead)
(function hookCatalogReveal(){
  const grid = document.getElementById('catalogGrid');
  if(!grid) return;
  const items = grid.querySelectorAll('.prod');
  if (typeof io !== 'undefined') items.forEach(el=> io.observe(el));
})();

// Фильтрация по категории, цене, поиску + сортировка
(function catalogLogic(){
  const grid = document.getElementById('catalogGrid');
  if(!grid) return;

  const search = document.getElementById('catalogSearch');
  const sortSel = document.getElementById('catalogSort');
  const chipsWrap = document.getElementById('catChips');
  const priceMin = document.getElementById('priceMin');
  const priceMax = document.getElementById('priceMax');
  const applyPrice = document.getElementById('applyPrice');
  const loadMore = document.getElementById('loadMore');

  let state = {
    cat: 'all',
    q: '',
    pmin: Number(priceMin?.value || 0),
    pmax: Number(priceMax?.value || 1e9),
    sort: 'pop',
    shown: 9 // сколько показываем сразу (демо-пагинация)
  };

  const items = Array.from(grid.querySelectorAll('.prod'));

  function normalizeName(s){ return (s||'').toString().toLowerCase().trim(); }

  function applyFilters(){
    const q = normalizeName(state.q);
    const filtered = items.filter(it=>{
      const catOk = state.cat === 'all' || it.dataset.cat === state.cat;
      const price = Number(it.dataset.price || 0);
      const priceOk = price >= state.pmin && price <= state.pmax;
      const nameOk = normalizeName(it.dataset.name).includes(q);
      return catOk && priceOk && nameOk;
    });

    // сортировка
    const sorted = filtered.sort((a,b)=>{
      if(state.sort === 'price_asc') return (a.dataset.price|0) - (b.dataset.price|0);
      if(state.sort === 'price_desc') return (b.dataset.price|0) - (a.dataset.price|0);
      if(state.sort === 'name_asc') return a.dataset.name.localeCompare(b.dataset.name,'ru');
      // popularity: чем меньше data-pop, тем популярнее
      return (a.dataset.pop|0) - (b.dataset.pop|0);
    });

    // пагинация (демо): показываем первые state.shown
    items.forEach(it=> it.style.display = 'none');
    sorted.slice(0, state.shown).forEach(it=> it.style.display = '');

    // кнопка "Показать ещё"
    if(loadMore){
      loadMore.style.display = sorted.length > state.shown ? '' : 'none';
      loadMore.onclick = ()=>{
        state.shown += 9;
        applyFilters();
      };
    }
  }

  // Слушатели
  if (chipsWrap){
    chipsWrap.addEventListener('click', (e)=>{
      const btn = e.target.closest('.chip');
      if(!btn) return;
      chipsWrap.querySelectorAll('.chip').forEach(c=>{c.classList.remove('active'); c.setAttribute('aria-selected','false');});
      btn.classList.add('active'); btn.setAttribute('aria-selected','true');
      state.cat = btn.dataset.cat || 'all';
      applyFilters();
    });
  }

  if(search){
    search.addEventListener('input', ()=>{
      state.q = search.value;
      applyFilters();
    });
  }

  if(sortSel){
    sortSel.addEventListener('change', ()=>{
      state.sort = sortSel.value;
      applyFilters();
    });
  }

  if(applyPrice){
    applyPrice.addEventListener('click', ()=>{
      state.pmin = Number(priceMin.value || 0);
      state.pmax = Number(priceMax.value || 1e9);
      applyFilters();
    });
  }

  // При переходе по якорю #catalog — фокус на заголовок для доступности
  if (location.hash === '#catalog'){
    const title = document.getElementById('catalog-title');
    if(title){ title.setAttribute('tabindex','-1'); title.focus({preventScroll:true}); }
  }

  // первый рендер
  applyFilters();
})();

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