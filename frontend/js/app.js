const API_URL = '/api/items';

const tbody = document.querySelector('#catalog-body');
const form = document.querySelector('.form');
const message = document.querySelector('#message');

function showMessage(text, color) {
    message.textContent = text;
    message.style.color = color;
}

// Побудова таблиці з масиву, отриманого із сервера
function renderTable(items) {
    tbody.innerHTML = '';

    items.forEach(function (item) {
        const row = document.createElement('tr');

        const titleCell = document.createElement('td');
        titleCell.textContent = item.title;

        const typeCell = document.createElement('td');
        typeCell.textContent = item.type;

        const yearCell = document.createElement('td');
        yearCell.textContent = item.year;

        const priceCell = document.createElement('td');
        priceCell.textContent = item.price;

        const purposeCell = document.createElement('td');
        purposeCell.textContent = item.purpose;

        const typicalCell = document.createElement('td');
        typicalCell.textContent = item.isTypical ? 'так' : 'ні';

        const actionCell = document.createElement('td');
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Видалити';
        deleteBtn.addEventListener('click', function () {
            deleteItem(item.id);
        });
        actionCell.append(deleteBtn);

        row.append(titleCell, typeCell, yearCell, priceCell, purposeCell, typicalCell, actionCell);
        tbody.append(row);
    });
}

// GET: завантаження списку
async function loadItems() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        renderTable(await response.json());
    } catch (error) {
        showMessage('Сервер не відповідає. Спробуйте пізніше.', 'red');
    }
}

// DELETE: видалення запису
async function deleteItem(id) {
    try {
        const response = await fetch(API_URL + '/' + id, { method: 'DELETE' });
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        showMessage('Запис видалено.', 'green');
        await loadItems();
    } catch (error) {
        showMessage('Не вдалося видалити запис. Сервер не відповідає.', 'red');
    }
}

loadItems();

// POST: додавання нового запису
form.addEventListener('submit', async function (event) {
    event.preventDefault();

    const title = document.querySelector('#name').value.trim();
    const type = document.querySelector('#type').value.trim();
    const year = Number(document.querySelector('#year').value);
    const price = Number(document.querySelector('#price').value);
    const purpose = document.querySelector('#purpose').value;
    const isTypical = document.querySelector('#is_typical').checked;

    message.textContent = '';

    if (title === '') {
        showMessage('Помилка: вкажіть назву виробу!', 'red');
        return;
    }
    if (type === '') {
        showMessage('Помилка: вкажіть тип кераміки!', 'red');
        return;
    }
    if (isNaN(year) || year < 1900 || year > 2026) {
        showMessage('Помилка: вкажіть коректний рік виготовлення (до 2026)!', 'red');
        return;
    }
    if (isNaN(price) || price <= 0) {
        showMessage('Помилка: ціна має бути більшою за 0!', 'red');
        return;
    }

    const newItem = { title, type, year, price, purpose, isTypical };

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newItem)
        });

        if (!response.ok) {
            const data = await response.json();
            const text = typeof data.detail === 'string' ? data.detail : 'Некоректні дані';
            showMessage('Помилка: ' + text, 'red');
            return;
        }

        form.reset();
        showMessage('Запис успішно додано до каталогу!', 'green');
        await loadItems();
    } catch (error) {
        showMessage('Сервер не відповідає. Спробуйте пізніше.', 'red');
    }
});