(function () {
    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : null;
    }

    document.addEventListener('DOMContentLoaded', function () {
        const editables = document.querySelectorAll('[data-edit]');
        editables.forEach(function (el) {
            el.setAttribute('contenteditable', 'true');
            el.classList.add('builder-editable');

            let original = el.innerText;

            el.addEventListener('focus', function () {
                original = el.innerText;
                el.classList.remove('builder-saved', 'builder-error');
            });

            el.addEventListener('blur', function () {
                const value = el.innerText;
                if (value === original) return;

                const [model, pk, field] = el.getAttribute('data-edit').split(':');
                fetch('/builder/save-field/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({ model: model, pk: pk, field: field, value: value }),
                })
                    .then(function (res) { return res.json().then(function (data) { return { ok: res.ok, data: data }; }); })
                    .then(function (result) {
                        if (result.ok && result.data.ok) {
                            el.classList.add('builder-saved');
                            setTimeout(function () { el.classList.remove('builder-saved'); }, 1200);
                        } else {
                            el.classList.add('builder-error');
                            el.innerText = original;
                        }
                    })
                    .catch(function () {
                        el.classList.add('builder-error');
                        el.innerText = original;
                    });
            });

            el.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' && el.dataset.editMultiline !== 'true') {
                    e.preventDefault();
                    el.blur();
                }
            });
        });
    });
})();
