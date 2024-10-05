window.API_URL = 'http://localhost:8000/api/v1';  // 끝의 슬래시 제거// 로그인 함수

// 모든 과목 가져오기
async function getAllCourses() {
    try {
        const response = await fetch(`${API_URL}/courses`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('과목을 불러오는데 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 과목 로드맵 가져오기
async function getCourseRoadmap() {
    try {
        const response = await fetch(`${API_URL}/courses/roadmap`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('로드맵을 불러오는데 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 과목 등록하기
async function enrollCourse(courseId) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}/enroll`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('과목 등록에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 새 과목 생성하기 (관리자용)
async function createCourse(courseData) {
    try {
        const response = await fetch(`${API_URL}/courses`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(courseData)
        });
        if (!response.ok) throw new Error('과목 생성에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 특정 과목 정보 가져오기
async function getCourse(courseId) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('과목 정보를 불러오는데 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 과목에 새 수업 추가하기 (관리자용)
async function addLessonToCourse(courseId, lessonData) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}/lessons`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(lessonData)
        });
        if (!response.ok) throw new Error('수업 추가에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 수업 정보 업데이트하기 (관리자용)
async function updateLesson(courseId, lessonId, lessonData) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}/lessons/${lessonId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(lessonData)
        });
        if (!response.ok) throw new Error('수업 업데이트에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 수업 삭제하기 (관리자용)
async function deleteLesson(courseId, lessonId) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}/lessons/${lessonId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('수업 삭제에 실패했습니다.');
        return true;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 수업 진행 상황 업데이트하기
async function updateLessonProgress(courseId, lessonId, progressData) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}/lessons/${lessonId}/progress`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(progressData)
        });
        if (!response.ok) throw new Error('진행 상황 업데이트에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 수업 진행 상황 가져오기
async function getLessonProgress(courseId, lessonId) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}/lessons/${lessonId}/progress`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('진행 상황을 불러오는데 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 과목 목록 표시
function displayCourses(courses) {
    const mainContent = document.getElementById('mainContent');
    let html = '<h2>과목 목록</h2><ul>';
    courses.forEach(course => {
        html += `
            <li>
                <h3>${course.title}</h3>
                <p>${course.description}</p>
                <button onclick="showCourseDetails(${course.id})">자세히 보기</button>
            </li>
        `;
    });
    html += '</ul>';
    mainContent.innerHTML = html;
}

// 과목 상세 정보 표시
function showCourseDetails(courseId) {
    getCourse(courseId).then(course => {
        const mainContent = document.getElementById('mainContent');
        let html = `
            <h2>${course.title}</h2>
            <p>${course.description}</p>
            <h3>수업 목록</h3>
            <ul>
        `;
        course.lessons.forEach(lesson => {
            html += `
                <li>
                    <h4>${lesson.title}</h4>
                    <p>${lesson.content}</p>
                    <button onclick="showLessonDetails(${course.id}, ${lesson.id})">수업 보기</button>
                </li>
            `;
        });
        html += '</ul>';
        mainContent.innerHTML = html;
    }).catch(error => {
        alert('과목 정보를 불러오는데 실패했습니다.');
    });
}

// 수업 상세 정보 가져오기
async function showLessonDetails(courseId, lessonId) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}/lessons/${lessonId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`수업 정보를 불러오는데 실패했습니다. 상태 코드: ${response.status}, 메시지: ${errorData.detail || '알 수 없는 오류'}`);
        }
        const lesson = await response.json();
        
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <h2>${lesson.title}</h2>
            <p>${lesson.content}</p>
            <video src="${lesson.video_url}" controls></video>
        `;
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 과목 업데이트하기 (관리자용)
async function updateCourse(courseId, courseData) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(courseData)
        });
        if (!response.ok) throw new Error('과목 업데이트에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 사용자별 과목 진행 상황 조회
async function getUserCourseProgress() {
    try {
        const response = await fetch(`${API_URL}/courses/user/progress`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('과목 진행 상황을 불러오는데 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 과목 검색
async function searchCourses(query) {
    try {
        const response = await fetch(`${API_URL}/courses/search?query=${encodeURIComponent(query)}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('과목 검색에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 인기 과목 목록 조회
async function getPopularCourses(limit = 10) {
    try {
        const response = await fetch(`${API_URL}/courses/popular?limit=${limit}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('인기 과목 목록을 불러오는데 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 과목 리뷰 작성
async function createCourseReview(courseId, reviewData) {
    try {
        const response = await fetch(`${API_URL}/courses/${courseId}/reviews`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reviewData)
        });
        if (!response.ok) throw new Error('리뷰 작성에 실패했습니다.');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 사용자 과목 진행 상황 표시
function displayUserCourseProgress(progressData) {
    const mainContent = document.getElementById('mainContent');
    let html = '<h2>내 학습 현황</h2><ul>';
    progressData.forEach(progress => {
        html += `
            <li>
                <h3>${progress.course_title}</h3>
                <p>진행률: ${progress.progress_percentage.toFixed(2)}%</p>
                <p>완료한 수업: ${progress.completed_lessons} / ${progress.total_lessons}</p>
            </li>
        `;
    });
    html += '</ul>';
    mainContent.innerHTML = html;
}

// 초기화 함수
function initCourses() {
    console.log('initCourses function called');
    getAllCourses().then(courses => {
        console.log('Courses received:', courses);
        displayCourses(courses);
    }).catch(error => {
        console.error('Error in initCourses:', error);
        alert(`과목 목록을 불러오는데 실패했습니다. 오류: ${error.message}`);
    });
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', initCourses);