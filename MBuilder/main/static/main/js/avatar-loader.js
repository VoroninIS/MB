document.getElementById('fileUpload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        // Показываем контейнер с Cropper
        document.getElementById('cropper-background').style.display = 'flex';
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
        document.body.style.overflow = 'hidden';
        document.body.style.paddingRight = `${scrollbarWidth}px`;
        
        // Инициализация Cropper
        const image = document.getElementById('cropperImage');
        image.src = event.target.result;
        
        if (window.cropper) window.cropper.destroy();
        
        window.cropper = new Cropper(image, {
            aspectRatio: 1,
            viewMode: 1,
            autoCropArea: 1,
            ready() {
                // При готовности создаем кнопку подтверждения
                const confirmButton = document.createElement('button');
                confirmButton.id = 'confirmCropBtn';
                confirmButton.textContent = 'Confirm';
                confirmButton.className = 'btn';
                confirmButton.style.marginTop = '40px';
                
                confirmButton.onclick = (e) => {
                    e.preventDefault();
                    
                    // Получаем обрезанное изображение
                    const canvas = cropper.getCroppedCanvas({
                        width: 512,
                        height: 512,
                    });

                    // Конвертируем в Blob
                    canvas.toBlob((blob) => {
                        // Создаем новый File объект
                        const croppedFile = new File([blob], file.name, {
                            type: blob.type,
                            lastModified: Date.now()
                        });

                        // Создаем DataTransfer для обновления input
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(croppedFile);
                        
                        // Обновляем input файл
                        document.getElementById('fileUpload').files = dataTransfer.files;

                        // Обновляем превью
                        document.getElementById('avatarPreview').src = URL.createObjectURL(blob);
                        
                        // Скрываем Cropper
                        document.getElementById('cropper-background').style.display = 'none';
                        cropper.destroy();
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }, 'image/jpeg', 0.9);
                };

                // Добавляем кнопку в контейнер
                if (!document.getElementById('confirmCropBtn')) {
                    document.getElementById('cropper-background').appendChild(confirmButton);
                }
            }
        });
    };
    reader.readAsDataURL(file);
    document.getElementById('save-button').style.display = 'block';
});

document.getElementById('cropper-background').addEventListener('click', function(e) {
    if (e.target === this) {
        this.style.display = 'none';
        if (window.cropper) {
            window.cropper.destroy();
            window.cropper = null;
        }
        const confirmBtn = document.getElementById('confirmCropBtn');
        if (confirmBtn) confirmBtn.remove();
        document.getElementById('save-button').style.display = 'none';
    }
});