/* ── Auth Logic ── */

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;

    /* ── Stepper Logic ── */
    window.currentStep = 1;
    window.goStep = function(target) {
        if (target > window.currentStep && !validateStep(window.currentStep)) return;
        document.querySelectorAll('.step-panel').forEach(p => p.classList.remove('active'));
        document.getElementById('panel-' + target).classList.add('active');
        document.querySelectorAll('.step-item').forEach(item => {
            const n = +item.dataset.step;
            const circle = item.querySelector('.step-circle');
            item.classList.remove('active', 'done');
            if (n === target) {
                item.classList.add('active');
                circle.textContent = n;
            } else if (n < target) {
                item.classList.add('done');
                circle.innerHTML = '<svg style="width:.85rem;height:.85rem" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>';
            } else {
                circle.textContent = n;
            }
        });
        window.currentStep = target;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    function showErr(id, show) {
        const el = document.getElementById(id);
        if (el) el.classList.toggle('visible', show);
    }
    function fieldErr(el, show) {
        if (el) el.classList.toggle('is-error', show);
    }

    function validateStep(step) {
        let ok = true;
        if (step === 1) {
            const tipo = document.getElementById('tipoDocumento');
            const doc = document.getElementById('docUsuario');
            const tOk = tipo.value.trim() !== '';
            const dOk = /^\d{5,15}$/.test(doc.value.trim());
            fieldErr(tipo, !tOk); showErr('tipo-error', !tOk);
            fieldErr(doc, !dOk); showErr('doc-error', !dOk);
            ok = tOk && dOk;
        } else if (step === 2) {
            const pn = document.getElementById('primerNombre');
            const pa = document.getElementById('primerApellido');
            const tel = document.getElementById('telefono');
            const em = document.getElementById('email');
            const pnOk = pn.value.trim() !== '';
            const paOk = pa.value.trim() !== '';
            const telOk = /^[0-9]{7,12}$/.test(tel.value.trim());
            const emOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em.value.trim());
            fieldErr(pn, !pnOk); showErr('pnombre-error', !pnOk);
            fieldErr(pa, !paOk); showErr('papellido-error', !paOk);
            fieldErr(tel, !telOk); showErr('tel-error', !telOk);
            fieldErr(em, !emOk); showErr('email-error', !emOk);
            ok = pnOk && paOk && telOk && emOk;
        }
        return ok;
    }

    /* ── Password requirements (always visible) ── */
    const pwInput = document.getElementById('password');
    const reqBox = document.getElementById('req-box');

    // Show requirements box immediately
    if (reqBox) {
        reqBox.classList.add('visible');
    }

    if (pwInput) {
        pwInput.addEventListener('input', () => {
            const v = pwInput.value;
            const lenEl = document.getElementById('req-length');
            const upEl = document.getElementById('req-upper');
            const numEl = document.getElementById('req-number');
            if (lenEl) lenEl.classList.toggle('valid', v.length >= 8);
            if (upEl) upEl.classList.toggle('valid', /[A-Z]/.test(v) && /[a-z]/.test(v));
            if (numEl) numEl.classList.toggle('valid', /\d/.test(v));
            updateStrength(v);
            checkMatch();
        });
    }

    function updateStrength(v) {
        let s = 0;
        if (v.length >= 8) s++;
        if (/[A-Z]/.test(v)) s++;
        if (/[a-z]/.test(v)) s++;
        if (/\d/.test(v)) s++;
        if (/[^A-Za-z0-9]/.test(v)) s++;
        const map = [
            { w: '0%', c: 'transparent', t: '—' },
            { w: '25%', c: '#f87171', t: 'Débil' },
            { w: '50%', c: '#fb923c', t: 'Regular' },
            { w: '75%', c: '#facc15', t: 'Buena' },
            { w: '100%', c: '#6ee7b7', t: 'Fuerte' },
        ];
        const m = map[Math.min(s, 4)];
        const bar = document.getElementById('strength-bar');
        const text = document.getElementById('strength-text');
        if (bar) {
            bar.style.width = m.w;
            bar.style.backgroundColor = m.c;
        }
        if (text) {
            text.textContent = m.t;
            text.style.color = m.c === 'transparent' ? 'var(--text-muted)' : m.c;
        }
    }

    /* ── Confirm match ── */
    const pwConfirm = document.getElementById('passwordConfirm');
    if (pwConfirm) {
        pwConfirm.addEventListener('input', checkMatch);
    }

    function checkMatch() {
        if (!pwConfirm || !pwInput) return;
        if (!pwConfirm.value) {
            pwConfirm.classList.remove('match', 'no-match');
            showErr('pw-match-err', false);
            return;
        }
        const match = pwInput.value === pwConfirm.value;
        pwConfirm.classList.toggle('match', match);
        pwConfirm.classList.toggle('no-match', !match);
        showErr('pw-match-err', !match);
    }

    /* ── Toggle visibility ── */
    window.togglePw = function(inputId, iconId) {
        const el = document.getElementById(inputId);
        const icon = document.getElementById(iconId);
        if (!el || !icon) return;
        const hidden = el.type === 'password';
        el.type = hidden ? 'text' : 'password';
        icon.innerHTML = hidden
            ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>'
            : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>';
    };

    /* ── Final submit guard ── */
    registerForm.addEventListener('submit', function(e) {
        console.log('Form submission started');
        
        if (!pwInput || !pwConfirm) {
            console.log('Password inputs not found');
            return;
        }
        
        const pw = pwInput.value;
        const pwConfirmValue = pwConfirm.value;
        
        // Check length
        const hasLength = pw.length >= 8;
        const hasUpper = /[A-Z]/.test(pw);
        const hasLower = /[a-z]/.test(pw);
        const hasNumber = /\d/.test(pw);
        const hasMatch = pw === pwConfirmValue;
        
        console.log('Password requirements check:', {
            hasLength, hasUpper, hasLower, hasNumber, hasMatch, 
            pwLength: pw.length, pwsMatch: pw === pwConfirmValue
        });
        
        const allReqs = hasLength && hasUpper && hasLower && hasNumber;
        
        if (!allReqs || !hasMatch) {
            e.preventDefault();
            console.log('Form submission blocked - requirements not met');
            
            if (!allReqs && reqBox) {
                reqBox.classList.add('visible');
                console.log('Showing requirement box');
            }
            if (!hasMatch) {
                showErr('pw-match-err', true);
                pwConfirm.classList.add('no-match');
                console.log('Password mismatch detected');
            }
            if (!hasUpper) console.log('Missing uppercase letter');
            if (!hasLower) console.log('Missing lowercase letter');
            if (!hasNumber) console.log('Missing number');
            if (!hasLength) console.log('Password too short');
        } else {
            console.log('Form submission allowed');
        }
    });
});
