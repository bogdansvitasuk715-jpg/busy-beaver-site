# Busy Beaver Handyman: сайт

## Як влаштовано
- `src/partials/`: спільні частини (шапка, низ, форма, іконки). Змінюєте раз, і зміна йде на всі сторінки.
- `src/content.py`: тексти сторінок послуг і міст.
- `src/pages/`: розділи головної сторінки.
- `assets/site.css`, `assets/site.js`: стилі й скрипти (тут же `CONFIG` з телефоном, email, знижкою).
- `build.py`: збирає сайт у `dist/`. Команда: `python3 build.py`.
- `netlify.toml`: Netlify сам запускає збірку і публікує `dist/`. Адреси без `.html`, наприклад `/services/tv-mounting`.
- `dist/sitemap.xml` і `robots.txt` створюються автоматично для Google.

Окремий бренд. Не має спільних фото, текстів, телефонів, email чи посилань з іншими сайтами.

## Готово
- Головна сторінка: усі розділи брифу a–j, мобільна панель «Call / Get a Quote».
- Логотип і маскот вирізані з прозорим фоном: `images/brand/`.
- Іконки сайту: `favicon-32.png`, `apple-touch-icon.png`.
- Розмітка LocalBusiness (schema.org) у `<head>`.
- Форма підготовлена під Netlify Forms (`data-netlify="true"`), разом із фото до 8 МБ.
- Спливаюче вікно «$50 OFF your first job»: через 6 секунд, один раз на відвідувача. Кнопка веде до форми й додає знижку в заявку. Текст і вимкнення: `CONFIG.offer`.
- Помічник «Ask Busy Beaver» у правому нижньому куті. Відповідає готовими відповідями за ключовими словами, без ШІ й без сервера.

## Замінити перед запуском
- `[PHONE]`: у блоці `CONFIG` у `assets/site.js` і в `src/partials/schema.html`. Поле `phoneTel` у форматі `+1XXXXXXXXXX`. Email уже стоїть: busybeaverky@gmail.com.
- `[DOMAIN]`: змінна `DOMAIN` у `build.py` і `src/partials/schema.html`.
- `liveForm: true`: увімкнути після публікації на Netlify. Далі в Netlify: Forms → Form notifications → Email, щоб заявки приходили на пошту.
- Відгуки: посилання «Leave a review» на сторінку Google і підключення Google-відгуків.

## Сторінки (29)
Головна, Services і 9 послуг, Service Areas і 7 міст, Blog і 6 статей, Property Managers, About, Contact.
Головна має галерею «до/після» (`images/work/`), блог бере статті з `src/blog.py`.
Далі: історія й справжні фото на About, умови для Property Managers, відгуки з Thumbtack.

## Фото
- Головний екран: `images/hero/hero-handyman.webp` (логотипи на фото замінені на справжні).
- Блог: `images/blog/<назва-статті>.webp`, послуги: `images/services/<назва>.webp`. Збірка підставляє їх сама. Запити для генерації в `IMAGE-PROMPTS.md`.
- About і «Our work»: лише справжні фото Busy Beaver.
