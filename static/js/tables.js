// static/js/tables.js
function calculateTableHeight() {
    // 1. Отримуємо висоту всього вікна браузера
    let windowHeight = window.innerHeight;

    // 2. Вираховуємо, скільки займають інші елементи (header, toolbar, footer)
    // Зазвичай це приблизно 200-250px залежно від вашого дизайну
    // Ви можете точно заміряти висоту вашої панелі з кнопками
    let offset = 230;

    let dynamicHeight = windowHeight - offset;

    // Встановлюємо мінімальну висоту, щоб таблиця не перетворилася на вузьку смужку
    return dynamicHeight < 200 ? 200 : dynamicHeight;
}

///========================================================================================================
function initDefaultDataTable(selector, customOptions = {}) {
    if ($(selector).length === 0) return;
    const defaultOptions = {
        "dom": 'lrtip',
        "pageLength": 25,
        "autoWidth": false,
        "scrollX": true,
        "scrollCollapse": true,
        // ВИКОРИСТОВУЄМО ФУНКЦІЮ ЗАМІСТЬ СТАТИЧНОГО VH
        "scrollY": calculateTableHeight() + "px",
        "language": {
        "decimal": "",
        "emptyTable": "Дані відсутні в таблиці",
        "info": "Показано з _START_ по _END_ із _TOTAL_ записів",
        "infoEmpty": "Показано з 0 по 0 із 0 записів",
        "infoFiltered": "(відфільтровано з _MAX_ записів)",
        "infoPostFix": "",
        "thousands": ",",
        "lengthMenu": "Показати _MENU_ записів",
        "loadingRecords": "Завантаження...",
        "processing": "Обробка...",
        "search": "",
        "zeroRecords": "Нічого не знайдено",
        "paginate": {
                        "first": "Перша",
                        "last": "Остання",
                        "next": "Наступна",
                        "previous": "Попередня"
                    },
    "aria": {
        "sortAscending": ": активуйте для сортування стовпців за зростанням",
        "sortDescending": ": активуйте для сортування стовпців за спаданням"
    }
},
        "order": [[0, "desc"]],
        "initComplete": function() {
            $(this).DataTable().columns.adjust();
        }
    };

    let table = $(selector).DataTable(Object.assign(defaultOptions, customOptions));

    // 3. АДАПТАЦІЯ ПРИ ЗМІНІ РОЗМІРУ ВІКНА (Resize)
    $(window).on('resize', function() {
        let newHeight = calculateTableHeight();
        // Оновлюємо внутрішній контейнер скролу DataTables
        $(selector).closest('.dataTables_scrollBody').css('height', newHeight + 'px');
        table.columns.adjust();
    });

    return table;
}
////=======================================================================================================

// Функція для копіювання (якщо вона вам потрібна всюди, де є таблиці)
function copyTable(selector = '#tList') {
    const el = document.querySelector(selector);
    if (!el) return;
    const range = document.createRange();
    range.selectNode(el);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    try {
        document.execCommand('copy');
        alert('Таблицю скопійовано!');
    } catch (err) {
        console.error('Не вдалося скопіювати', err);
    }
    window.getSelection().removeAllRanges();
}

$(document).ready(function() {
    $('#tList').DataTable({
        "paging": true,
        "lengthMenu": [ [10, 25, 30, 50, -1], [10, 25,30, 50, "Всі"] ],
        "pageLength": 25,
        "autoWidth": false,
        "language": {
            "search": "",
            "searchPlaceholder": "Пошук тексту",
            "lengthMenu": "Показати _MENU_",
            "info": "Записи з _START_ по _END_ (всього _TOTAL_)",
            "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/uk.json"
        }
    });
});

//$(document).ready(function() {
//    // Викликаємо вашу функцію для конкретної таблиці
//    initDefaultDataTable('#tList');
//});