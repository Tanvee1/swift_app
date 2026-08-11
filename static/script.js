// SwiftShop Global State & Helpers

let shelf = JSON.parse(localStorage.getItem('swift_shelf') || '[]');

document.addEventListener('DOMContentLoaded', () => {
  updateShelfUI();
  setupDrawerListeners();
});

function saveShelf() {
  localStorage.setItem('swift_shelf', JSON.stringify(shelf));
  updateShelfUI();
}

function toggleShelf(itemName, price, category, image) {
  const index = shelf.findIndex(item => item.name === itemName);
  if (index === -1) {
    shelf.push({ name: itemName, price: price || '', category: category || '', image: image || '' });
    showToast(`Added "${itemName}" to shelf`);
  } else {
    shelf.splice(index, 1);
    showToast(`Removed "${itemName}" from shelf`);
  }
  saveShelf();
}

function removeShelfItem(itemName) {
  shelf = shelf.filter(item => item.name !== itemName);
  showToast(`Removed "${itemName}" from shelf`);
  saveShelf();
}

function isShelved(itemName) {
  return shelf.some(item => item.name === itemName);
}

function updateShelfUI() {
  const badges = document.querySelectorAll('.shelf-count-badge');
  badges.forEach(b => b.textContent = shelf.length);

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
  if (drawerList) {
    if (shelf.length === 0) {
      drawerList.innerHTML = '<div class="empty-shelf">Your shelf is empty.<br>Click "+ Shelve" on any product to save it here!</div>';
    } else {
      drawerList.innerHTML = shelf.map(item => `
        <li class="shelf-item">
          <div class="shelf-item-info">
            <h4>${item.name}</h4>
            <p>${item.price ? '₹' + item.price : ''} ${item.category ? '• ' + item.category : ''}</p>
          </div>
          <button class="btn-remove" onclick="removeShelfItem('${item.name.replace(/'/g, "\\'")}')" title="Remove">✕</button>
        </li>
      `).join('');
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
