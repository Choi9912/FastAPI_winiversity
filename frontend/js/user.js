window.API_URL = 'http://localhost:8000/api/v1';

// 현재 사용자 정보를 가져오는 함수
async function getCurrentUser() {
    try {
        const response = await fetch(`${API_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('사용자 정보를 가져오는데 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 사용자 프로필 표시
async function showUserProfile() {
    try {
        const user = await getCurrentUser();
        const mainContent = document.getElementById('mainContent');
        
        if (user.role === 'ADMIN') {
            // 관리자 대시보드 표시
            showAdminDashboard();
        } else {
            mainContent.innerHTML = `
                <h2>사용자 프로필</h2>
                <p>사용자명: ${user.username}</p>
                <p>이메일: ${user.email}</p>
                <p>닉네임: ${user.nickname}</p>
                <button onclick="showUpdateProfileForm()">프로필 업데이트</button>
                <button onclick="confirmDeleteAccount()">계정 삭제</button>
            `;
        }
    } catch (error) {
        console.error('Error showing user profile:', error);
        alert('프로필을 표시하는데 실패했습니다.');
    }
}

// 프로필 링크 클릭 이벤트 처리
function handleProfileClick(e) {
    e.preventDefault();
    showUserProfile();
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    const profileLink = document.getElementById('profileLink');
    if (profileLink) {
        profileLink.addEventListener('click', handleProfileClick);
    }
});

// 로그인 상태 확인 및 UI 업데이트
async function checkLoginStatus() {
    const token = localStorage.getItem('token');
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const profileLink = document.getElementById('profileLink');
    const logoutLink = document.getElementById('logoutLink');

    if (token) {
        try {
            const user = await getCurrentUser();
            loginLink.style.display = 'none';
            registerLink.style.display = 'none';
            profileLink.style.display = 'inline';
            logoutLink.style.display = 'inline';
            profileLink.textContent = user.role === 'ADMIN' ? '관리자 대시보드' : `${user.username}의 프로필`;
        } catch (error) {
            console.error('Error checking login status:', error);
            localStorage.removeItem('token');
        }
    } else {
        loginLink.style.display = 'inline';
        registerLink.style.display = 'inline';
        profileLink.style.display = 'none';
        logoutLink.style.display = 'none';
    }
}

// 사용자 프로필 업데이트 함수
async function updateUserProfile(userData) {
    try {
        const response = await fetch(`${API_URL}/users/me`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        if (!response.ok) throw new Error('프로필 업데이트에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error updating profile:', error);
        throw error;
    }
}

// 사용자 계정 삭제 함수
async function deleteUserAccount() {
    try {
        const response = await fetch(`${API_URL}/users/me`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('계정 삭제에 실패했습니다.');
        return true;
    } catch (error) {
        console.error('Error deleting account:', error);
        throw error;
    }
}

// 프로필 업데이트 폼 표시
function showUpdateProfileForm() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <h2>프로필 업데이트</h2>
        <form id="updateProfileForm">
            <label for="nickname">닉네임:</label>
            <input type="text" id="nickname" name="nickname" required><br><br>
            <button type="submit">업데이트</button>
        </form>
    `;
    document.getElementById('updateProfileForm').addEventListener('submit', handleProfileUpdate);
}

// 프로필 업데이트 처리
async function handleProfileUpdate(event) {
    event.preventDefault();
    const nickname = document.getElementById('nickname').value;
    try {
        await updateUserProfile({ nickname });
        alert('프로필이 성공적으로 업데이트되었습니다.');
        showUserProfile();
    } catch (error) {
        console.error('Error updating profile:', error);
        alert('프로필 업데이트에 실패했습니다.');
    }
}

// 계정 삭제 확인
function confirmDeleteAccount() {
    if (confirm('정말로 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
        handleAccountDeletion();
    }
}

// 계정 삭제 처리
async function handleAccountDeletion() {
    try {
        await deleteUserAccount();
        alert('계정이 성공적으로 삭제되었습니다.');
        localStorage.removeItem('token');
        window.location.href = '/login.html';
    } catch (error) {
        console.error('Error deleting account:', error);
        alert('계정 삭제에 실패했습니다.');
    }
}

// 페이지 로드 시 사용자 프로필 표시
document.addEventListener('DOMContentLoaded', showUserProfile);