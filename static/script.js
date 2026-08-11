// SwiftShop Production E-Commerce Engine & State Management

let shelf = JSON.parse(localStorage.getItem('swift_shelf') || '[]');

document.addEventListener('DOMContentLoaded', () => {
  updateShelfUI();
  setupDrawerListeners();
  setupAutocompleteSearch();
});

function saveShelf() {
  localStorage.setItem('swift_shelf', JSON.stringify(shelf));
  updateShelfUI();
}

function toggleShelf(itemName, price, category, image, productId) {
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

function clearShelf() {
  shelf = [];
  showToast("Shelf cleared");
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

      // Fetch Cart calculation from API backend
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
