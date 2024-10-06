// frontend/js/mission.js

window.API_URL = 'http://localhost:8000/api/v1';  // 실제 백엔드 URL로 변경하세요

let missions = []; // 모든 미션 정보를 저장할 전역 변수

function loadMissions() {
    console.log('Loading missions...');
    fetch(`${window.API_URL}/missions`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) throw new Error('Failed to load missions');
        return response.json();
    })
    .then(data => {
        console.log('Missions data:', data);
        missions = data;
        showMissionList(); // 미션 로드 후 목록 표시
    })
    .catch(error => {
        console.error('Error loading missions:', error);
        alert('미션 목록을 불러오는데 실패했습니다.');
    });
}

function displayMissions(missions) {
    console.log('Displaying missions:', missions);
    let missionList = document.getElementById('missionList');
    if (!missionList) {
        console.log('missionList element not found, creating it');
        const mainContent = document.getElementById('mainContent');
        if (mainContent) {
            mainContent.innerHTML = '<div id="missionList"></div>';
            missionList = document.getElementById('missionList');
        } else {
            console.error('mainContent element not found');
            return;
        }
    }
    missionList.innerHTML = '<h2>미션 목록</h2>';
    if (missions.length === 0) {
        missionList.innerHTML += '<p>표시할 미션이 없습니다.</p>';
        return;
    }
    missions.forEach(mission => {
        console.log('Rendering mission:', mission);
        const missionElement = document.createElement('div');
        missionElement.innerHTML = `
            <h3>${mission.question}</h3>
            <p>과목: ${mission.course}</p>
            <p>유형: ${mission.type}</p>
            <button class="mission-view-btn" data-mission-id="${mission.id}">미션 보기</button>
        `;
        missionList.appendChild(missionElement);
    });

    // 미션 보기 버튼에 이벤트 리스너 추가
    const missionViewButtons = document.querySelectorAll('.mission-view-btn');
    missionViewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const missionId = this.getAttribute('data-mission-id');
            console.log(`Clicked mission ID: ${missionId}`);
            showMission(missionId);
        });
    });
}

async function showMission(missionId) {
    console.log(`showMission called with ID: ${missionId}`);
    try {
        console.log(`API_URL: ${window.API_URL}`);
        if (!window.API_URL) {
            throw new Error('API_URL is not defined');
        }

        const url = `${window.API_URL}/missions/${missionId}`;
        console.log(`Fetching from URL: ${url}`);

        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No token found in localStorage');
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const mission = await response.json();
        console.log('Fetched mission:', mission);
        displayMissionDetail(mission);
    } catch (error) {
        console.error('Error in showMission:', error);
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            console.log('Network error or CORS issue. Check your API_URL and server CORS settings.');
        }
        alert(`미션 정보를 불러오는데 실패했습니다. 오류: ${error.message}`);
    }
}

function displayMissionDetail(mission) {
    console.log('Displaying mission detail:', mission);
    const missionDetail = document.getElementById('missionDetail');
    console.log('missionDetail element:', missionDetail);
    if (!missionDetail) {
        console.error('Error: missionDetail element not found');
        return;
    }

    // HTML 콘텐츠을 구성합니다.
    let html = `
        <h2>${mission.question}</h2>
        <p>과목: ${mission.course}</p>
        <p>유형: ${mission.type}</p>
    `;

    if (mission.type === 'multiple_choice') {
        console.log('Rendering multiple choice question');
        html += `
            <form id="multipleChoiceForm">
                ${mission.multiple_choice.options.map((option, index) => `
                    <div>
                        <input type="radio" id="option${index}" name="selected_option" value="${index}">
                        <label for="option${index}">${option}</label>
                    </div>
                `).join('')}
                <button type="submit">제출</button>
            </form>
        `;
    } else if (mission.type === 'code_submission') {
        console.log('Rendering code submission question');
        html += `
            <h3>문제 설명</h3>
            <p>${mission.code_submission.problem_description}</p>
            <h3>코드 작성</h3>
            <div id="editor" style="height: 300px;">${mission.code_submission.initial_code || ''}</div>
            <button id="submitCode">코드 제출</button>
        `;
    }

    html += `
        <div id="result"></div>
        <button onclick="displayMissions()">미션 목록으로 돌아가기</button>
    `;

    // innerHTML을 한 번에 설정하여 HTML 구조의 무결성을 유지합니다.
    missionDetail.innerHTML = html;

    // 이벤트 리스너를 추가합니다.
    if (mission.type === 'multiple_choice') {
        const form = document.getElementById('multipleChoiceForm');
        if (form) {
            form.addEventListener('submit', (e) => submitMultipleChoice(e, mission.id));
        }
    } else if (mission.type === 'code_submission') {
        const editor = ace.edit("editor");
        editor.setTheme("ace/theme/monokai");
        editor.session.setMode("ace/mode/python");
        const submitCodeBtn = document.getElementById('submitCode');
        if (submitCodeBtn) {
            submitCodeBtn.addEventListener('click', () => submitCode(mission.id, editor.getValue()));
        }
    }

    // 미션 목록을 숨기고, 미션 상세 정보를 표시합니다.
    document.getElementById('missionList').style.display = 'none';
    missionDetail.style.display = 'block';
    console.log('Mission detail rendering completed');
}

// 다른 함수들 (submitMultipleChoice, submitCode, displayResult)은 기존 코드와 동일하게 유지
function showMissionList() {
    console.log('Showing mission list');
    const missionSection = document.getElementById('missionSection');
    const missionList = document.getElementById('missionList');
    const missionDetail = document.getElementById('missionDetail');
    
    if (missionSection) {
        missionSection.style.display = 'block';
    } else {
        console.error('missionSection element not found');
        return;
    }
    
    if (missionList) {
        missionList.style.display = 'block';
    } else {
        console.error('missionList element not found');
        return;
    }
    
    if (missionDetail) {
        missionDetail.style.display = 'none';
    } else {
        console.error('missionDetail element not found');
        return;
    }
    
    displayMissions(missions);
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded in mission.js');
    
    const missionLink = document.getElementById('missionLink');
    if (missionLink) {
        missionLink.addEventListener('click', (e) => {
            e.preventDefault();
            showMissionList();
        });
    } else {
        console.error('missionLink element not found');
    }
    
    // 초기 미션 로드
    loadMissions();
});