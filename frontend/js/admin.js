window.API_URL = 'http://localhost:8000/api/v1';

// 모든 사용자 정보 가져오기
async function getAllUsers() {
    try {
        const response = await fetch(`${API_URL}/admin/users`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('사용자 목록을 가져오는데 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 특정 사용자 정보 가져오기
async function getUserById(userId) {
    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}`, {
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

// 관리자 대시보드 표시
function showAdminDashboard() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <h2>관리자 대시보드</h2>
        <button onclick="showAllUsers()">모든 사용자 보기</button>
        <button onclick="showCourseManagement()">과목 관리</button>
        <button onclick="showMissionManagement()">미션 관리</button>
        <button onclick="showAddCourseForm()">새 과목 추가</button>
        <button onclick="showAddMissionForm()">새 미션 추가</button>
        <div id="adminContent"></div>
    `;
}

// 모든 사용자 목록 표시
async function showAllUsers() {
    try {
        const users = await getAllUsers();
        const userList = document.getElementById('userList');
        userList.innerHTML = '<h3>사용자 목록</h3><ul>';
        users.forEach(user => {
            userList.innerHTML += `<li>${user.username} (ID: ${user.id}) - <button onclick="showUserDetails(${user.id})">상세 정보</button></li>`;
        });
        userList.innerHTML += '</ul>';
    } catch (error) {
        console.error('Error showing all users:', error);
        alert('사용자 목록을 표시하는데 실패했습니다.');
    }
}

// 특정 사용자의 상세 정보 표시
async function showUserDetails(userId) {
    try {
        const user = await getUserById(userId);
        const userList = document.getElementById('userList');
        userList.innerHTML = `
            <h3>사용자 상세 정보</h3>
            <p>ID: ${user.id}</p>
            <p>Username: ${user.username}</p>
            <p>Email: ${user.email}</p>
            <p>Nickname: ${user.nickname}</p>
            <p>Role: ${user.role}</p>
            <button onclick="showAllUsers()">목록으로 돌아가기</button>
        `;
    } catch (error) {
        console.error('Error showing user details:', error);
        alert('사용자 상세 정보를 표시하는데 실패했습니다.');
    }
}

// 과목 관리 인터페이스 표시
function showCourseManagement() {
    const adminContent = document.getElementById('adminContent');
    adminContent.innerHTML = `
        <h3>과목 관리</h3>
        <button onclick="showAddCourseForm()">새 과목 추가</button>
        <div id="courseList"></div>
    `;
    loadCourses();
}

// 새 과목 추가 폼 표시
function showAddCourseForm() {
    const adminContent = document.getElementById('adminContent');
    adminContent.innerHTML = `
        <h3>새 과목 추가</h3>
        <form id="addCourseForm">
            <input type="text" id="courseTitle" placeholder="과목 제목" required>
            <textarea id="courseDescription" placeholder="과목 설명" required></textarea>
            <input type="number" id="courseOrder" placeholder="순서" required>
            <label><input type="checkbox" id="courseIsPaid"> 유료 과목</label>
            <input type="number" id="coursePrice" placeholder="가격" disabled>
            <button type="submit">과목 추가</button>
        </form>
    `;
    document.getElementById('addCourseForm').addEventListener('submit', handleAddCourse);
    document.getElementById('courseIsPaid').addEventListener('change', togglePriceInput);
}

// 가격 입력 필드 토글
function togglePriceInput() {
    const isPaid = document.getElementById('courseIsPaid').checked;
    const priceInput = document.getElementById('coursePrice');
    priceInput.disabled = !isPaid;
    if (!isPaid) priceInput.value = '';
}

// 과목 추가 처리
async function handleAddCourse(event) {
    event.preventDefault();
    const courseData = {
        title: document.getElementById('courseTitle').value,
        description: document.getElementById('courseDescription').value,
        order: parseInt(document.getElementById('courseOrder').value),
        is_paid: document.getElementById('courseIsPaid').checked,
        price: document.getElementById('courseIsPaid').checked ? parseFloat(document.getElementById('coursePrice').value) : 0,
        lessons: []
    };

    try {
        const response = await fetch(`${API_URL}/courses`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(courseData)
        });
        if (!response.ok) throw new Error('과목 추가에 실패했습니다.');
        alert('과목이 성공적으로 추가되었습니다.');
        showCourseManagement();
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 미션 관리 인터페이스 표시
function showMissionManagement() {
    const adminContent = document.getElementById('adminContent');
    adminContent.innerHTML = `
        <h3>미션 관리</h3>
        <button onclick="showAddMissionForm()">새 미션 추가</button>
        <div id="missionList"></div>
    `;
    loadMissions();
}

// 새 미션 추가 폼 표시
function showAddMissionForm() {
    const adminContent = document.getElementById('adminContent');
    adminContent.innerHTML = `
        <h3>새 미션 추가</h3>
        <form id="addMissionForm">
            <select id="missionCourse" required>
                <option value="">과목 선택</option>
            </select>
            <input type="text" id="missionQuestion" placeholder="문제" required>
            <select id="missionType" required>
                <option value="multiple_choice">객관식</option>
                <option value="code_submission">코드 제출</option>
            </select>
            <select id="missionExamType" required>
                <option value="midterm">중간고사</option>
                <option value="final">기말고사</option>
            </select>
            <div id="missionTypeSpecificFields"></div>
            <button type="submit">미션 추가</button>
        </form>
        <button onclick="showAdminDashboard()">관리자 대시보드로 돌아가기</button>
    `;
    document.getElementById('addMissionForm').addEventListener('submit', handleAddMission);
    document.getElementById('missionType').addEventListener('change', updateMissionTypeFields);
    loadCoursesForMissionForm();
}

// 미션 유형에 따른 필드 업데이트
function updateMissionTypeFields() {
    const missionType = document.getElementById('missionType').value;
    const specificFields = document.getElementById('missionTypeSpecificFields');
    
    if (missionType === 'multiple_choice') {
        specificFields.innerHTML = `
            <input type="text" id="missionOptions" placeholder="선택지 (쉼표로 구분)" required>
            <input type="text" id="missionCorrectAnswer" placeholder="정답" required>
        `;
    } else if (missionType === 'code_submission') {
        specificFields.innerHTML = `
            <textarea id="missionProblemDescription" placeholder="문제 설명" required></textarea>
            <textarea id="missionInitialCode" placeholder="초기 코드"></textarea>
            <textarea id="missionTestCases" placeholder="테스트 케이스 (JSON 형식)" required></textarea>
        `;
    }
}

// 과목 목록 로드 (미션 폼용)
async function loadCoursesForMissionForm() {
    try {
        const response = await fetch(`${API_URL}/courses`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('과목 목록을 불러오는데 실패했습니다.');
        const courses = await response.json();
        const courseSelect = document.getElementById('missionCourse');
        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = course.title;
            courseSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 미션 추가 처리
async function handleAddMission(event) {
    event.preventDefault();
    const missionData = {
        course: document.getElementById('missionCourse').value,
        question: document.getElementById('missionQuestion').value,
        type: document.getElementById('missionType').value,
        exam_type: document.getElementById('missionExamType').value
    };

    if (missionData.type === 'multiple_choice') {
        missionData.multiple_choice = {
            options: document.getElementById('missionOptions').value.split(',').map(option => option.trim()),
            correct_answer: document.getElementById('missionCorrectAnswer').value.trim()
        };
    } else if (missionData.type === 'code_submission') {
        missionData.code_submission = {
            problem_description: document.getElementById('missionProblemDescription').value,
            initial_code: document.getElementById('missionInitialCode').value,
            test_cases: JSON.parse(document.getElementById('missionTestCases').value)
        };
    }

    console.log('Sending mission data:', JSON.stringify(missionData, null, 2));

    try {
        const response = await fetch(`${API_URL}/missions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(missionData)
        });
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error response:', errorText);
            throw new Error(`미션 추가에 실패했습니다. 서버 응답: ${errorText}`);
        }
        const result = await response.json();
        console.log('Server response:', result);
        alert('미션이 성공적으로 추가되었습니다.');
        showMissionManagement();
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 페이지 로드 시 관리자 대시보드 표시
document.addEventListener('DOMContentLoaded', showAdminDashboard);

// 미션 목록 로드
async function loadMissions() {
    try {
        console.log('Fetching missions...');
        const response = await fetch(`${API_URL}/missions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        console.log('Response status:', response.status);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to fetch missions: ${response.status} ${errorText}`);
        }
        const missions = await response.json();
        console.log('Missions:', missions);
        displayMissions(missions);
    } catch (error) {
        console.error('Error in loadMissions:', error);
        alert(`미션 목록을 가져오는데 실패했습니다: ${error.message}`);
    }
}