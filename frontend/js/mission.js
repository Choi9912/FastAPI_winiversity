window.API_URL = 'http://localhost:8000/api/v1';

// 미션 목록 가져오기
async function loadMissions() {
    try {
        const response = await fetch(`${API_URL}/missions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('미션 목록을 가져오는데 실패했습니다.');
        const missions = await response.json();
        displayMissions(missions);
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 미션 목록 표시
function displayMissions(missions) {
    const missionList = document.getElementById('missionList');
    missionList.innerHTML = '<h2>미션 목록</h2>';
    missions.forEach(mission => {
        missionList.innerHTML += `
            <div>
                <h3>${mission.question}</h3>
                <p>과목: ${mission.course}</p>
                <p>유형: ${mission.type}</p>
                <button onclick="showMission(${mission.id})">미션 보기</button>
            </div>
        `;
    });
}

// 개별 미션 표시
async function showMission(missionId) {
    try {
        const response = await fetch(`${API_URL}/missions/${missionId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('미션을 가져오는데 실패했습니다.');
        const mission = await response.json();
        displayMissionDetail(mission);
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 미션 상세 정보 표시
function displayMissionDetail(mission) {
    const missionDetail = document.getElementById('missionDetail');
    missionDetail.innerHTML = `
        <h2>${mission.question}</h2>
        <p>과목: ${mission.course}</p>
        <p>유형: ${mission.type}</p>
    `;

    if (mission.type === 'multiple_choice') {
        missionDetail.innerHTML += `
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
        document.getElementById('multipleChoiceForm').addEventListener('submit', (e) => submitMultipleChoice(e, mission.id));
    } else if (mission.type === 'code_submission') {
        missionDetail.innerHTML += `
            <h3>문제 설명</h3>
            <p>${mission.code_submission.problem_description}</p>
            <h3>코드 작성</h3>
            <div id="editor" style="height: 300px;">${mission.code_submission.initial_code}</div>
            <button id="submitCode">코드 제출</button>
        `;
        const editor = ace.edit("editor");
        editor.setTheme("ace/theme/monokai");
        editor.session.setMode("ace/mode/javascript");
        document.getElementById('submitCode').addEventListener('click', () => submitCode(mission.id, editor.getValue()));
    }

    missionDetail.innerHTML += `
        <div id="result"></div>
        <button onclick="loadMissions()">미션 목록으로 돌아가기</button>
    `;
}

// 객관식 답안 제출
async function submitMultipleChoice(event, missionId) {
    event.preventDefault();
    const selectedOption = document.querySelector('input[name="selected_option"]:checked');
    if (!selectedOption) {
        alert('답안을 선택해주세요.');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/missions/${missionId}/submit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ selected_option: parseInt(selectedOption.value) })
        });
        if (!response.ok) throw new Error('답안 제출에 실패했습니다.');
        const result = await response.json();
        displayResult(result);
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 코드 제출
async function submitCode(missionId, code) {
    try {
        const response = await fetch(`${API_URL}/missions/${missionId}/submit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        });
        if (!response.ok) throw new Error('코드 제출에 실패했습니다.');
        const result = await response.json();
        displayResult(result);
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 결과 표시
function displayResult(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <h3>제출 결과</h3>
        <p>${result.is_correct ? '정답입니다!' : '틀렸습니다. 다시 시도해보세요.'}</p>
    `;
    if (result.output) {
        resultDiv.innerHTML += `
            <h4>실행 결과:</h4>
            <pre>${result.output}</pre>
        `;
    }
}

// 페이지 로드 시 미션 목록 표시
document.addEventListener('DOMContentLoaded', loadMissions);