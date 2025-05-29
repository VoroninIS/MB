$('.generate-button').click(function () {
    const $errorBlock = $('.error-messages');
    $errorBlock.hide().empty();
    
    const prompt = $('.prompt-field').val().trim();
    
    // Предварительная валидация на клиенте
    if (!prompt) {
        $errorBlock.html('The prompt field cannot be empty.').show();
        return;
    }
    
    // Проверка на недопустимые символы (опционально, дублируем серверную)
    const invalidChars = prompt.match(/[^a-zA-Zа-яА-Я0-9\s_\-.,!?()":%+\/=]/g);
    if (invalidChars) {
        const uniqueChars = [...new Set(invalidChars)];
        $errorBlock.html(
            `Invalid characters: ${uniqueChars.join(', ')}. ` +
            'Allowed: letters, numbers, spaces and _-.,!?()":%+/='
        ).show();
        return;
    }

    let filename = prompt
        .split(/\s+/)
        .slice(0, 3)
        .join('_')
        // Разрешаем допустимые символы
        .replace(/[^a-zA-Zа-яА-ЯёЁ0-9_\-]/gi, '') 
        .replace(/_+/g, '_');    // Убрать множественные подчеркивания

    // Если имя пустое после обработки
    if (!filename.trim()) filename = 'unnamed_schem';
    // Добавляем временную метку для уникальности
    filename += '_' + Date.now();

    $.ajax({
        type: 'GET',
        url: 'schem_generation',
        data: {'prompt': prompt},
        xhrFields: {responseType: 'blob'},
        success: function(data) {
            // Создаем временную ссылку для скачивания
            const url = window.URL.createObjectURL(data);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename + '.schem' || 'generated_file.schem';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        },
        error: function(xhr) {
            if (xhr.status === 400) {
                // Обработка ошибок валидации
                try {
                    const errors = JSON.parse(xhr.responseText).errors;
                    let errorHtml = '';
                    
                    for (let field in errors) {
                        errors[field].forEach(error => {
                            errorHtml += `<div>${error.message}</div>`;
                        });
                    }
                    
                    $errorBlock.html(errorHtml).show();
                } catch(e) {
                    $errorBlock.html('Request processing error').show();
                }
            } else {
                $errorBlock.html(`An error has occurred: ${xhr.statusText}`).show();
            }
        }
    });
});