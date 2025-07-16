document.addEventListener('DOMContentLoaded', () => {
    // 獲取所有需要的 DOM 元素
    const uploadSection = document.getElementById('upload-section');
    const confirmSection = document.getElementById('confirm-section');
    const recipeSection = document.getElementById('recipe-section');
    const loader = document.getElementById('loader');
    const loaderText = document.getElementById('loader-text');
    
    const fileInputs = document.querySelectorAll('.file-input');
    const identifyBtn = document.getElementById('identify-btn');
    const generateBtn = document.getElementById('generate-btn');

    let identifiedIngredients = [];

    // 處理圖片預覽
    fileInputs.forEach(input => {
        input.addEventListener('change', event => {
            const file = event.target.files[0];
            if (file) {
                const preview = document.getElementById(`preview${input.id.slice(-1)}`);
                preview.src = URL.createObjectURL(file);
                preview.style.display = 'block';
            }
        });
    });

    // 點擊「辨識食材」按鈕
    identifyBtn.addEventListener('click', async () => {
        const formData = new FormData();
        let fileCount = 0;
        fileInputs.forEach(input => {
            if (input.files[0]) {
                formData.append('images', input.files[0]);
                fileCount++;
            }
        });

        if (fileCount === 0) {
            alert('請至少上傳一張冰箱照片！');
            return;
        }

        showLoader('AI 主廚正在掃描您的冰箱...');

        try {
            const response = await fetch('/api/identify-ingredients', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();

            if (data.success) {
                identifiedIngredients = data.ingredients;
                displayIngredients(identifiedIngredients);
                switchSection(confirmSection);
            } else {
                alert('食材辨識失敗，請再試一次。');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('發生錯誤，請檢查後端伺服器是否運行。');
        } finally {
            hideLoader();
        }
    });

    // 點擊「生成食譜」按鈕
    generateBtn.addEventListener('click', async () => {
        showLoader('AI 主廚正在發揮創意...');

        try {
            const response = await fetch('/api/generate-recipe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ingredients: identifiedIngredients }),
            });
            const data = await response.json();

            if (data.success) {
                displayRecipe(data.recipe);
                switchSection(recipeSection);
            } else {
                alert(`食譜生成失敗：${data.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('發生錯誤，無法生成食譜。');
        } finally {
            hideLoader();
        }
    });

    // --- 輔助函式 ---

    function showLoader(text) {
        loaderText.textContent = text;
        loader.style.display = 'flex';
    }

    function hideLoader() {
        loader.style.display = 'none';
    }

    function switchSection(activeSection) {
        [uploadSection, confirmSection, recipeSection].forEach(s => s.classList.remove('active'));
        activeSection.classList.add('active');
    }

    function displayIngredients(ingredients) {
        const tagsContainer = document.getElementById('ingredient-tags');
        tagsContainer.innerHTML = ingredients.map(ing => `<div class="tag">${ing}</div>`).join('');
    }

    function displayRecipe(recipe) {
        recipeSection.innerHTML = `
            <h2 class="recipe-title">${recipe.title}</h2>
            <p class="recipe-description">${recipe.description}</p>
            <div class="recipe-meta">
                <div><strong>準備:</strong> ${recipe.prep_time}</div>
                <div><strong>烹飪:</strong> ${recipe.cook_time}</div>
                <div><strong>份量:</strong> ${recipe.servings}</div>
            </div>
            <div class="recipe-details">
                <div class="ingredients-list">
                    <h3>主要食材</h3>
                    <ul>${recipe.ingredients.map(i => `<li>${i.name} - ${i.quantity}</li>`).join('')}</ul>
                    <h3>調味料</h3>
                    <ul>${recipe.seasonings.map(s => `<li>${s.name} - ${s.quantity}</li>`).join('')}</ul>
                </div>
                <div class="steps-list">
                    <h3>料理步驟</h3>
                    <ol>${recipe.steps.map(step => `<li>${step}</li>`).join('')}</ol>
                </div>
            </div>
            <div class="chef-tip" style="margin-top: 2rem; background: #fffbe6; padding: 1rem; border-radius: 8px; border-left: 4px solid #fcc419;">
                <strong>主廚小提示:</strong> ${recipe.chef_tip}
            </div>
        `;
    }
});