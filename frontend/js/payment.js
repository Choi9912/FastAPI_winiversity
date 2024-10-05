window.API_URL = 'http://localhost:8000/api/v1';

async function fetchCourses() {
    const response = await fetch(`${API_URL}/courses`);
    if (!response.ok) {
        throw new Error('코스 정보를 가져오는데 실패했습니다.');
    }
    return await response.json();
}

async function createPaymentSection() {
    const mainContent = document.getElementById('mainContent');
    if (!mainContent) {
        console.error('mainContent not found');
        return;
    }

    const paymentSection = document.createElement('div');
    paymentSection.id = 'paymentSection';
    paymentSection.style.display = 'none';

    try {
        const courses = await fetchCourses();
        const courseOptions = courses.map(course => 
            `<option value="${course.id}">${course.name} - ${course.price}원</option>`
        ).join('');

        paymentSection.innerHTML = `
            <h1>결제 페이지</h1>
            <select id="course-select">
                <option value="">코스를 선택하세요</option>
                ${courseOptions}
            </select>
            <input type="text" id="coupon-code" placeholder="쿠폰 코드 입력">
            <button id="apply-coupon">쿠폰 적용</button>
            <button id="payment-button" disabled>결제하기</button>
        `;

        mainContent.appendChild(paymentSection);
        console.log('Payment section created');
    } catch (error) {
        console.error('Error creating payment section:', error);
        paymentSection.innerHTML = '<p>코스 정보를 불러오는데 실패했습니다.</p>';
        mainContent.appendChild(paymentSection);
    }
}

async function initPayment() {
    console.log('Payment initialization started');
    const paymentSection = document.getElementById('paymentSection');
    const courseSelect = document.getElementById('course-select');
    const paymentButton = document.getElementById('payment-button');
    const couponInput = document.getElementById('coupon-code');
    const applyCouponButton = document.getElementById('apply-coupon');

    if (!paymentSection) console.error('paymentSection not found');
    if (!courseSelect) console.error('course-select not found');
    if (!paymentButton) console.error('payment-button not found');
    if (!couponInput) console.error('coupon-code not found');
    if (!applyCouponButton) console.error('apply-coupon not found');

    if (!paymentSection || !courseSelect || !paymentButton || !couponInput || !applyCouponButton) {
        console.error('필요한 요소를 찾을 수 없습니다.');
        return;
    }

    courseSelect.addEventListener('change', function() {
        paymentButton.disabled = !this.value;
    });

    paymentButton.addEventListener('click', handlePayment);
    applyCouponButton.addEventListener('click', applyCoupon);
}

async function handlePayment() {
    const courseId = document.getElementById('course-select').value;
    if (!courseId) {
        alert('코스를 선택해주세요.');
        return;
    }

    try {
        const paymentData = await preparePayment(courseId);
        const portOneResponse = await requestPortOnePayment(paymentData);

        if (portOneResponse.code === "PAYMENT_SUCCESS") {
            await confirmPayment(portOneResponse, courseId, paymentData);
        } else {
            throw new Error('결제 실패');
        }
    } catch (error) {
        alert('결제에 실패했습니다: ' + error.message);
        console.log("결제 실패", error);
    }
}

async function preparePayment(courseId, couponCode = null) {
    const response = await fetch(`${API_URL}/payments/prepare`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            course_id: parseInt(courseId),
            method: 'CARD',
            coupon_code: couponCode
        }),
    });

    if (!response.ok) {
        throw new Error('결제 준비 실패');
    }

    const paymentData = await response.json();
    console.log('Prepared payment data:', paymentData);
    
    if (!paymentData.totalAmount || isNaN(paymentData.totalAmount) || paymentData.totalAmount <= 0) {
        throw new Error('유효하지 않은 결제 금액입니다.');
    }

    return paymentData;
}

async function requestPortOnePayment(paymentData) {
    return await PortOne.requestPayment({
        storeId: paymentData.storeId,
        channelGroupId: paymentData.channelGroupId,
        paymentId: paymentData.paymentId,
        orderName: paymentData.orderName,
        totalAmount: paymentData.totalAmount,
        currency: paymentData.currency,
        payMethod: paymentData.payMethod,
        customer: paymentData.customer,
    });
}

async function confirmPayment(portOneResponse, courseId, paymentData) {
    const response = await fetch(`${API_URL}/payments/confirm`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            imp_uid: portOneResponse.imp_uid,
            merchant_uid: portOneResponse.merchant_uid,
            course_id: parseInt(courseId),
            amount: paymentData.totalAmount,
            method: paymentData.payMethod
        }),
    });

    if (!response.ok) {
        throw new Error('결제 확인 실패');
    }

    const confirmResult = await response.json();
    alert('결제가 성공적으로 완료되었습니다.');
    console.log("결제 성공", confirmResult);
}

async function applyCoupon() {
    const courseId = document.getElementById('course-select').value;
    const couponCode = document.getElementById('coupon-code').value;

    if (!courseId) {
        alert('코스를 선택해주세요.');
        return;
    }

    if (!couponCode) {
        alert('쿠폰 코드를 입력해주세요.');
        return;
    }

    try {
        const paymentData = await preparePayment(courseId, couponCode);
        alert(`쿠폰이 적용되었습니다. 할인 금액: ${paymentData.discountAmount}원`);
    } catch (error) {
        alert('쿠폰 적용에 실패했습니다: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', initPayment);