// ====================
// Auth Modal
// ====================
const modal = document.getElementById('authModal');
const loginSection = document.getElementById('loginFormSection');
const signupSection = document.getElementById('signupFormSection');

function showModal(type) {
    if (modal) {
        modal.classList.add('active');
        switchForm(type);
    }
}

function closeModal() {
    if (modal) modal.classList.remove('active');
}

function switchForm(type) {
    if (!loginSection || !signupSection) return;
    if (type === 'signup') {
        loginSection.classList.add('hidden');
        signupSection.classList.remove('hidden');
    } else {
        signupSection.classList.add('hidden');
        loginSection.classList.remove('hidden');
    }
}

if (modal) {
    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeModal();
    });
}

// ====================
// Auto-hide Messages
// ====================
const messageBox = document.getElementById('messageBox');
if (messageBox) {
    setTimeout(() => {
        messageBox.style.opacity = '0';
        setTimeout(() => messageBox.remove(), 300);
    }, 5000);
}

// ====================
// Confirm Modal
// ====================
let confirmCallback = null;

function showConfirm(title, message, callback) {
    const overlay = document.getElementById('confirmModal');
    const titleEl = document.getElementById('confirmTitle');
    const messageEl = document.getElementById('confirmMessage');

    if (!overlay || !titleEl || !messageEl) return;

    titleEl.textContent = title;
    messageEl.textContent = message;
    confirmCallback = callback;

    overlay.classList.add('active');
}

function closeConfirm() {
    const overlay = document.getElementById('confirmModal');
    if (overlay) overlay.classList.remove('active');
    confirmCallback = null;
}

function confirmYes() {
    if (confirmCallback) confirmCallback();
    closeConfirm();
}

function confirmNo() {
    closeConfirm();
}

// ====================
// Material Modal
// ====================
function openMaterial(type, url, title, downloadUrl) {
    console.log('📦 openMaterial called:', { type, url, title, downloadUrl });

    const modalEl = document.getElementById('materialModal');
    const modalBody = document.getElementById('materialModalBody');
    const modalTitle = document.getElementById('materialModalTitle');
    const modalIcon = document.getElementById('materialModalIcon');
    const modalFooter = document.getElementById('materialModalFooter');

    if (!modalEl || !modalBody || !modalTitle) {
        console.error('❌ Modal elements not found!');
        return;
    }

    modalTitle.textContent = title || 'ماتېرىيال';

    let content = '';
    let iconClass = 'fas fa-file';
    let showDownloadButton = false;

    if (type === 'video' && url) {
        iconClass = 'fas fa-video';
        content = `
            <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden; background: #000;">
                <iframe src="${url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen referrerpolicy="strict-origin-when-cross-origin" frameborder="0"></iframe>
            </div>
        `;
    }
    else if (type === 'pdf' && url) {
        iconClass = 'fas fa-file-pdf';
        content = `
            <div style="padding: 20px; background: #f8fafc; min-height: 500px;">
                <object data="${url}" type="application/pdf" style="width: 100%; height: 70vh; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <div style="padding: 40px; text-align: center; background: white; border-radius: 8px;">
                        <p style="color: #64748b; margin-bottom: 20px;">PDF كۆرگۈچىڭىزدا قوللىمايدۇ</p>
                        <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                            <a href="${url}" target="_blank" style="background: #0d5c5f; color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;"><i class="fas fa-external-link-alt"></i> يېڭى tab دا ئېچىش</a>
                            <a href="${url}" download style="background: #eab308; color: #0f172a; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;"><i class="fas fa-download"></i> چۈشۈرۈش</a>
                        </div>
                    </div>
                </object>
            </div>
        `;
        showDownloadButton = true;
    }
    else if (type === 'image' && url) {
        iconClass = 'fas fa-image';
        content = `
            <div style="display: flex; justify-content: center; align-items: center; min-height: 500px; padding: 20px; background: #f8fafc;">
                <img src="${url}" alt="${title}" style="max-width: 100%; max-height: 80vh; object-fit: contain; border-radius: 8px;">
            </div>
        `;
        showDownloadButton = true;
    }
    else if (type === 'doc' && url) {
        iconClass = 'fas fa-file-word';
        content = `
            <div style="padding: 60px 20px; text-align: center; background: #f8fafc; min-height: 500px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div style="font-size: 5rem; margin-bottom: 20px; color: #2563eb;">📝</div>
                <h3 style="color: #1e293b; margin-bottom: 10px;">Word ھۆججەت</h3>
                <p style="color: #64748b; margin-bottom: 30px; font-size: 1rem; max-width: 500px; line-height: 1.8;">Word ھۆججەتلىرىنى بىۋاسىتە توربەتتە كۆرگىلى بولمايدۇ. ھۆججەتنى چۈشۈرۈپ كومپيۇتېرىڭىزدا ئېچىڭ.</p>
                <a href="${url}" download style="background: #0d5c5f; color: white; padding: 14px 40px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-flex; align-items: center; gap: 10px;"><i class="fas fa-download"></i> ھۆججەتنى چۈشۈرۈش</a>
            </div>
        `;
    }
    else if (url) {
        iconClass = 'fas fa-download';
        content = `
            <div style="padding: 60px 20px; text-align: center; background: #f8fafc; min-height: 500px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div style="font-size: 5rem; margin-bottom: 20px;">📦</div>
                <h3 style="color: #1e293b; margin-bottom: 10px;">${title}</h3>
                <p style="color: #64748b; margin-bottom: 30px;">بۇ ھۆججەتنى چۈشۈرۈپ كۆرۈڭ</p>
                <a href="${url}" download style="background: #0d5c5f; color: white; padding: 14px 40px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 1.1rem;"><i class="fas fa-download"></i> چۈشۈرۈش</a>
            </div>
        `;
    }
    else {
        content = `
            <div style="padding: 60px 20px; text-align: center; background: #f8fafc; min-height: 500px;">
                <div style="font-size: 5rem; margin-bottom: 20px;">⚠️</div>
                <h3 style="color: #1e293b;">مەزمۇن تېپىلمىدى</h3>
            </div>
        `;
    }

    if (modalIcon) modalIcon.className = iconClass;
    modalBody.innerHTML = content;

    if (modalFooter) {
        if (showDownloadButton && downloadUrl) {
            modalFooter.innerHTML = `
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">📄 ${title}</p>
                <a href="${downloadUrl}" download style="background: #0d5c5f; color: white; padding: 8px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 0.9rem;"><i class="fas fa-download"></i> چۈشۈرۈش</a>
            `;
        } else {
            modalFooter.innerHTML = `<p style="margin: 0; color: #64748b; font-size: 0.9rem;">${title}</p>`;
        }
    }

    modalEl.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMaterialModal() {
    const modalEl = document.getElementById('materialModal');
    if (!modalEl) return;

    modalEl.classList.remove('active');
    document.body.style.overflow = '';

    setTimeout(() => {
        const modalBody = document.getElementById('materialModalBody');
        if (modalBody) modalBody.innerHTML = '';
    }, 300);
}

// ====================
// FAQ Accordion (GLOBAL scope - مۇھىم!)
// ====================
function toggleFaq(button) {
    const answer = button.nextElementSibling;
    const icon = button.querySelector('.faq-icon');
    const isOpen = answer.style.maxHeight && answer.style.maxHeight !== '0px';

    document.querySelectorAll('.faq-answer').forEach(item => {
        item.style.maxHeight = '0';
    });
    document.querySelectorAll('.faq-icon').forEach(item => {
        item.style.transform = 'rotate(0deg)';
    });

    if (!isOpen) {
        answer.style.maxHeight = answer.scrollHeight + 'px';
        icon.style.transform = 'rotate(180deg)';
    }
}

// ====================
// Escape Key Handler
// ====================
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeMaterialModal();
        closeModal();
        closeConfirm();
    }
});