const cartCount = document.querySelector('#cart-count');
const cartDialog = document.querySelector('#cart-dialog');
const cartItemsList = document.querySelector('#cart-items');
const cartEmptyMessage = document.querySelector('#cart-empty');
const cartSubtotal = document.querySelector('#cart-subtotal');
const cartNotice = document.querySelector('#cart-notice');
const themeToggle = document.querySelector('#theme-toggle');
const cart = loadCart();
let noticeTimeout;

function readStorage(key, fallback) {
    try {
        const value = localStorage.getItem(key);
        return value === null ? fallback : value;
    } catch {
        return fallback;
    }
}

function writeStorage(key, value) {
    try {
        localStorage.setItem(key, value);
    } catch {
        return;
    }
}

function loadCart() {
    try {
        const savedCart = JSON.parse(readStorage('store-cart', '[]'));
        if (!Array.isArray(savedCart)) return [];

        return savedCart.filter((item) => (
            item && typeof item.name === 'string' &&
            Number.isFinite(item.price) && Number.isInteger(item.quantity) &&
            item.quantity > 0
        ));
    } catch {
        return [];
    }
}

function saveCart() {
    writeStorage('store-cart', JSON.stringify(cart));
}

function renderCart() {
    const itemCount = cart.reduce((total, item) => total + item.quantity, 0);
    const subtotal = cart.reduce((total, item) => total + item.price * item.quantity, 0);
    cartCount.textContent = String(itemCount);
    cartItemsList.replaceChildren();
    cartEmptyMessage.hidden = cart.length > 0;
    cartSubtotal.textContent = `$${subtotal.toFixed(2)}`;

    for (const item of cart) {
        const row = document.createElement('li');
        const details = document.createElement('div');
        const name = document.createElement('span');
        const quantity = document.createElement('span');
        const price = document.createElement('strong');
        const remove = document.createElement('button');

        row.className = 'cart-item';
        name.className = 'cart-item-name';
        name.textContent = item.name;
        quantity.className = 'cart-item-detail';
        quantity.textContent = `Qty ${item.quantity}`;
        price.textContent = `$${(item.price * item.quantity).toFixed(2)}`;
        remove.className = 'cart-item-remove';
        remove.type = 'button';
        remove.textContent = 'Remove';
        remove.setAttribute('aria-label', `Remove ${item.name} from cart`);
        remove.dataset.removeProduct = item.name;

        details.append(name, quantity);
        row.append(details, price, remove);
        cartItemsList.append(row);
    }

    document.querySelector('.cart-continue').hidden = cart.length === 0;
}

function showNotice(message) {
    cartNotice.textContent = message;
    cartNotice.classList.add('is-visible');
    clearTimeout(noticeTimeout);
    noticeTimeout = setTimeout(() => cartNotice.classList.remove('is-visible'), 2400);
}

function setTheme(isDark) {
    document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
    themeToggle.checked = isDark;
    writeStorage('store-theme', isDark ? 'dark' : 'light');
}

document.querySelector('.products').addEventListener('click', (event) => {
    const button = event.target.closest('.btn');
    const product = button?.closest('.product');
    if (!product) return;

    const name = product.querySelector('h2').textContent.trim();
    const price = Number(product.querySelector('strong').textContent.replace(/[^\d.]/g, ''));
    const existingItem = cart.find((item) => item.name === name);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ name, price, quantity: 1 });
    }

    saveCart();
    renderCart();
    showNotice(`${name} added to your cart.`);
});

document.querySelector('#cart-open').addEventListener('click', (event) => {
    event.preventDefault();
    renderCart();
    cartDialog.showModal();
});

document.querySelector('.cart-close').addEventListener('click', () => cartDialog.close());
document.querySelector('.cart-continue').addEventListener('click', () => cartDialog.close());

cartItemsList.addEventListener('click', (event) => {
    const button = event.target.closest('[data-remove-product]');
    if (!button) return;

    const itemIndex = cart.findIndex((item) => item.name === button.dataset.removeProduct);
    if (itemIndex !== -1) cart.splice(itemIndex, 1);
    saveCart();
    renderCart();
});

cartDialog.addEventListener('click', (event) => {
    if (event.target === cartDialog) cartDialog.close();
});

themeToggle.addEventListener('change', () => setTheme(themeToggle.checked));

setTheme(readStorage('store-theme', 'light') === 'dark');
renderCart();