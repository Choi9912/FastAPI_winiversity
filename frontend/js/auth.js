window.API_URL = 'http://localhost:8000/api/v1';  // 끝의 슬래시 제거// 로그인 함수
async function login(username, password) {
    try {
        const response = await fetch(`${API_URL}/auth/token`, {  // URL 앞의 슬래시 제거
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        });

        console.log('Login response status:', response.status);  // 디버깅 로그 추가

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            alert('로그인 성공');
            updateUI(true);
        } else {
            const errorData = await response.json();
            alert(`로그인 실패: ${errorData.detail || '알 수 없는 오류'}`);
        }
    } catch (error) {
        console.error('로그인 중 오류 발생:', error);
        alert('로그인 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
}

// 회원가입 함수
async function register(username, email, password, nickname, phone_number) {
    const userData = {
        username,
        email,
        password,
        nickname,
        phone_number,
        is_active: true,
        role: 'STUDENT'
    };
    console.log('Sending user data:', userData);

    try {
        const registerUrl = `${API_URL}/auth/register`;
        console.log('Attempting registration with URL:', registerUrl);  // 디버깅 로그 추가

        const response = await fetch(registerUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Server response:', errorData);
            throw new Error(errorData.detail || '알 수 없는 오류');
        }

        const data = await response.json();
        console.log('Server response:', data);
        alert('회원가입이 완료되었습니다. 로그인해주세요.');
        showLoginForm();
    } catch (error) {
        console.error('회원가입 중 오류 발생:', error);
        alert(`회원가입 실패: ${error.message}`);
    }
}

// 로그아웃 함수
function logout() {
    localStorage.removeItem('token');
    updateUI(false);
    alert('로그아웃되었습니다.');
}

// UI 업데이트 함수
function updateUI(isLoggedIn) {
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const profileLink = document.getElementById('profileLink');
    const logoutLink = document.getElementById('logoutLink');

    if (isLoggedIn) {
        loginLink.style.display = 'none';
        registerLink.style.display = 'none';
        profileLink.style.display = 'inline';
        logoutLink.style.display = 'inline';
    } else {
        loginLink.style.display = 'inline';
        registerLink.style.display = 'inline';
        profileLink.style.display = 'none';
        logoutLink.style.display = 'none';
    }
}

// 로그인 폼 표시
function showLoginForm() {
    console.log('Showing login form');
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <h2>로그인</h2>
        <form id="loginForm">
            <div class="form-group">
                <label for="username">사용자명:</label>
                <input type="text" id="username" required>
            </div>
            <div class="form-group">
                <label for="password">비밀번호:</label>
                <input type="password" id="password" required>
            </div>
            <button type="submit">로그인</button>
        </form>
    `;

    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        await login(username, password);
    });
}

// 회원가입 폼 표시
function showRegisterForm() {
    console.log('Showing register form');
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <h2>회원가입</h2>
        <form id="registerForm">
            <div class="form-group">
                <label for="regUsername">사용자명:</label>
                <input type="text" id="regUsername" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="regEmail">이메일:</label>
                <input type="email" id="regEmail" required autocomplete="email">
            </div>
            <div class="form-group">
                <label for="regPassword">비밀번호:</label>
                <input type="password" id="regPassword" required autocomplete="new-password">
            </div>
            <div class="form-group">
                <label for="regNickname">닉네임:</label>
                <input type="text" id="regNickname" required autocomplete="nickname">
            </div>
            <div class="form-group">
                <label for="regPhoneNumber">전화번호:</label>
                <input type="tel" id="regPhoneNumber" required autocomplete="tel">
            </div>
            <button type="submit">회원가입</button>
        </form>
    `;

    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const nickname = document.getElementById('regNickname').value;
        const phone_number = document.getElementById('regPhoneNumber').value;

        await register(username, email, password, nickname, phone_number);
    });
}

// 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', () => {
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const logoutLink = document.getElementById('logoutLink');

    loginLink.addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
    });

    registerLink.addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterForm();
    });

    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        logout();
    });

    // 초기 UI 설정
    updateUI(localStorage.getItem('token') !== null);
});

// 관리자 기능은 별도의 파일로 분리하는 것이 좋습니다.