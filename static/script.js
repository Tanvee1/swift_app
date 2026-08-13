// SwiftShop Production E-Commerce Engine & Theme State Management

let shelf = JSON.parse(localStorage.getItem('swift_shelf') || '[]');

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  updateShelfUI();
  setupDrawerListeners();
  setupAutocompleteSearch();
  setupQuickViewModal();
});

/* Theme Management */
function initTheme() {
  const savedTheme = localStorage.getItem('swift_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  setTheme(savedTheme);

  const toggleBtn = document.getElementById('themeToggleBtn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      setTheme(newTheme);
      showToast(`Switched to ${newTheme} mode`);
    });
  }
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('swift_theme', theme);

  const toggleBtn = document.getElementById('themeToggleBtn');
  if (toggleBtn) {
    toggleBtn.innerHTML = theme === 'dark' 
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
    toggleBtn.setAttribute('title', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
  }
}

/* Shelf Management */
function saveShelf() {
  localStorage.setItem('swift_shelf', JSON.stringify(shelf));
  updateShelfUI();
}

function toggleShelf(itemName, price, category, image, productId, stockStatus) {
  if (stockStatus && stockStatus !== 'In Stock') {
    showToast(`"${itemName}" is currently Out of Stock`);
    return;
  }
  const index = shelf.findIndex(item => item.name === itemName);
  if (index === -1) {
    shelf.push({ 
      productId: productId || Date.now(),
      name: itemName, 
      price: parseFloat(price) || 0, 
      quantity: 1,
      category: category || '', 
      image: image || '' 
    });
    showToast(`Added "${itemName}" to shelf`);
  } else {
    shelf.splice(index, 1);
    showToast(`Removed "${itemName}" from shelf`);
  }
  saveShelf();
}

function changeQuantity(itemName, delta) {
  const item = shelf.find(i => i.name === itemName);
  if (item) {
    item.quantity += delta;
    if (item.quantity <= 0) {
      removeShelfItem(itemName);
    } else {
      saveShelf();
    }
  }
}

function removeShelfItem(itemName) {
  shelf = shelf.filter(item => item.name !== itemName);
  showToast(`Removed "${itemName}" from shelf`);
  saveShelf();
}

function isShelved(itemName) {
  return shelf.some(item => item.name === itemName);
}

async function updateShelfUI() {
  const badges = document.querySelectorAll('.shelf-count-badge');
  const totalCount = shelf.reduce((sum, item) => sum + (item.quantity || 1), 0);
  badges.forEach(b => b.textContent = totalCount);

  const buttons = document.querySelectorAll('[data-shelf-item]');
  buttons.forEach(btn => {
    if (btn.disabled) return;
    const itemName = btn.getAttribute('data-shelf-item');
    if (isShelved(itemName)) {
      btn.classList.add('shelved');
      btn.innerHTML = '✓ Shelved';
    } else {
      btn.classList.remove('shelved');
      btn.innerHTML = '+ Shelve';
    }
  });

  const drawerList = document.getElementById('drawerShelfList');
  const cartSummary = document.getElementById('cartSummaryContainer');

  if (drawerList) {
    if (shelf.length === 0) {
      drawerList.innerHTML = '<div class="empty-shelf">Your shelf is empty.<br>Click "+ Shelve" on any product to add items here!</div>';
      if (cartSummary) cartSummary.style.display = 'none';
    } else {
      drawerList.innerHTML = shelf.map(item => `
        <li class="shelf-item">
          <div class="shelf-item-info">
            <h4>${escapeHtml(item.name)}</h4>
            <p>₹${item.price} ${item.category ? '• ' + escapeHtml(item.category) : ''}</p>
          </div>
          <div class="shelf-qty-controls">
            <button class="btn-qty" onclick="changeQuantity('${escapeJs(item.name)}', -1)">-</button>
            <span class="qty-val">${item.quantity || 1}</span>
            <button class="btn-qty" onclick="changeQuantity('${escapeJs(item.name)}', 1)">+</button>
            <button class="btn-remove" onclick="removeShelfItem('${escapeJs(item.name)}')" title="Remove">✕</button>
          </div>
        </li>
      `).join('');

      try {
        const res = await fetch('/api/cart/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items: shelf })
        });
        const cartData = await res.json();
        
        if (cartSummary) {
          cartSummary.style.display = 'block';
          cartSummary.innerHTML = `
            <div class="cart-summary-card">
              <div class="summary-row"><span>Subtotal:</span> <strong>₹${cartData.subtotal}</strong></div>
              <div class="summary-row"><span>Estimated GST (5%):</span> <strong>₹${cartData.tax}</strong></div>
              <div class="summary-row"><span>Delivery Fee:</span> <strong>${cartData.delivery_fee === 0 ? 'FREE' : '₹' + cartData.delivery_fee}</strong></div>
              <hr class="summary-divider">
              <div class="summary-row grand-total"><span>Grand Total:</span> <strong>₹${cartData.grand_total}</strong></div>
              <button class="btn-checkout" onclick="alert('Order placed successfully! Total: ₹${cartData.grand_total}')">Checkout Now</button>
            </div>
          `;
        }
      } catch (err) {
        console.error("Cart Calculation error:", err);
      }
    }
  }
}

function setupDrawerListeners() {
  const trigger = document.getElementById('shelfTriggerBtn');
  const backdrop = document.getElementById('drawerBackdrop');
  const closeBtn = document.getElementById('drawerCloseBtn');
  const drawer = document.getElementById('shelfDrawer');

  if (trigger && drawer && backdrop) {
    trigger.addEventListener('click', () => {
      drawer.classList.add('open');
      backdrop.classList.add('active');
    });

    const close = () => {
      drawer.classList.remove('open');
      backdrop.classList.remove('active');
    };

    if (closeBtn) closeBtn.addEventListener('click', close);
    backdrop.addEventListener('click', close);
  }
}

function setupAutocompleteSearch() {
  const searchInput = document.querySelector('.search-box input[name="q"]');
  if (!searchInput) return;

  const wrapper = searchInput.parentElement;
  let dropdown = document.getElementById('searchAutocomplete');
  if (!dropdown) {
    dropdown = document.createElement('div');
    dropdown.id = 'searchAutocomplete';
    dropdown.className = 'autocomplete-dropdown';
    wrapper.appendChild(dropdown);
  }

  let debounceTimer;
  searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim();
    if (query.length < 2) {
      dropdown.style.display = 'none';
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/products?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (data.products && data.products.length > 0) {
          dropdown.style.display = 'block';
          dropdown.innerHTML = data.products.slice(0, 5).map(p => `
            <a href="/chat?q=${encodeURIComponent(p.name)}" class="autocomplete-item">
              <div>
                <span class="auto-title">${escapeHtml(p.name)}</span>
                <span class="auto-cat">${escapeHtml(p.category)} • ${escapeHtml(p.location)}</span>
              </div>
              <span class="auto-price">₹${p.price}</span>
            </a>
          `).join('');
        } else {
          dropdown.style.display = 'none';
        }
      } catch (err) {
        console.error("Autocomplete error:", err);
      }
    }, 250);
  });

  document.addEventListener('click', (e) => {
    if (!wrapper.contains(e.target)) {
      dropdown.style.display = 'none';
    }
  });
}

function setupQuickViewModal() {
  let modalBackdrop = document.getElementById('productModalBackdrop');
  if (!modalBackdrop) {
    modalBackdrop = document.createElement('div');
    modalBackdrop.id = 'productModalBackdrop';
    modalBackdrop.className = 'modal-backdrop';
    modalBackdrop.innerHTML = `
      <div class="modal-card">
        <div class="modal-header">
          <span class="card-category" id="modalCategory">CATEGORY</span>
          <button class="close-btn" id="modalCloseBtn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="modal-img-wrap">
            <img id="modalImg" src="" alt="Product">
          </div>
          <div class="modal-details">
            <h3 id="modalTitle">Product Title</h3>
            <div class="modal-price" id="modalPrice">₹0</div>
            <p id="modalDesc" style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.2rem;"></p>
            <div style="display: flex; gap: 0.6rem; align-items: center; margin-bottom: 1.5rem;">
              <span class="aisle-tag" id="modalLocation">Aisle 1</span>
              <span class="badge-stock in-stock" id="modalStock" style="position: static;">In Stock</span>
              <span class="rating-pill" id="modalRating" style="position: static;">★ 4.8</span>
            </div>
            <button class="btn-shelve" id="modalShelveBtn">+ Shelve</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modalBackdrop);

    const close = () => modalBackdrop.classList.remove('active');
    document.getElementById('modalCloseBtn').addEventListener('click', close);
    modalBackdrop.addEventListener('click', (e) => {
      if (e.target === modalBackdrop) close();
    });
  }

  document.addEventListener('click', async (e) => {
    const cardImg = e.target.closest('.card-img-wrap');
    const cardTitle = e.target.closest('.card-title');
    const targetEl = cardImg || cardTitle;

    if (targetEl) {
      const card = targetEl.closest('.card');
      if (!card) return;

      const title = card.querySelector('.card-title')?.textContent;
      const price = card.querySelector('.price')?.textContent;
      const category = card.querySelector('.card-category')?.textContent;
      const desc = card.querySelector('.card-desc')?.textContent;
      const location = card.querySelector('.aisle-tag')?.textContent;
      const imgSrc = card.querySelector('img')?.src;
      const shelveBtn = card.querySelector('.btn-shelve');
      const itemName = shelveBtn?.getAttribute('data-shelf-item') || title;

      document.getElementById('modalTitle').textContent = title;
      document.getElementById('modalPrice').textContent = price;
      document.getElementById('modalCategory').textContent = category;
      document.getElementById('modalDesc').textContent = desc;
      document.getElementById('modalLocation').textContent = location;
      document.getElementById('modalImg').src = imgSrc;

      const mShelveBtn = document.getElementById('modalShelveBtn');
      if (shelveBtn && shelveBtn.disabled) {
        mShelveBtn.disabled = true;
        mShelveBtn.innerHTML = 'Out of Stock';
        mShelveBtn.onclick = null;
      } else if (isShelved(itemName)) {
        mShelveBtn.disabled = false;
        mShelveBtn.classList.add('shelved');
        mShelveBtn.innerHTML = '✓ Shelved';
      } else {
        mShelveBtn.disabled = false;
        mShelveBtn.classList.remove('shelved');
        mShelveBtn.innerHTML = '+ Shelve';
      }

      if (!mShelveBtn.disabled) {
        mShelveBtn.onclick = () => {
          toggleShelf(itemName, price.replace('₹', ''), category, imgSrc.split('/').pop());
          if (isShelved(itemName)) {
            mShelveBtn.classList.add('shelved');
            mShelveBtn.innerHTML = '✓ Shelved';
          } else {
            mShelveBtn.classList.remove('shelved');
            mShelveBtn.innerHTML = '+ Shelve';
          }
        };
      }

      modalBackdrop.classList.add('active');
    }
  });
}

function showToast(message) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 2500);
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, s => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[s]));
}

function escapeJs(str) {
  return String(str).replace(/'/g, "\\'");
}
