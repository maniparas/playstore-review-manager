const form = document.getElementById('filters-form');
const reviewsTableBody = document.querySelector('#reviews-table tbody');
const summaryTotal = document.getElementById('summary-total');
const summaryAverage = document.getElementById('summary-average');
const summarySentiment = document.getElementById('summary-sentiment');
const summaryRecency = document.getElementById('summary-recency');
const keywordsList = document.getElementById('keywords-list');
const aiBriefBlock = document.getElementById('ai-brief');
const aiBriefContainer = document.querySelector('.ai-brief-container');
const alertPlaceholder = document.getElementById('alerts');

const spinner = document.querySelector('.loading-indicator');

const sentimentEmoji = {
  positive: '😊',
  neutral: '😐',
  negative: '🙁'
};

async function fetchReviews(event) {
  event?.preventDefault();
  spinner.style.display = 'inline-flex';
  alertPlaceholder.innerHTML = '';

  const formData = new FormData(form);
  const params = new URLSearchParams();
  for (const [key, value] of formData.entries()) {
    if (value) {
      params.append(key, value);
    }
  }

  try {
    const response = await fetch(`/api/reviews?${params.toString()}`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch reviews');
    }
    const payload = await response.json();
    renderSummary(payload.summary);
    renderReviews(payload.reviews);
  } catch (error) {
    showAlert(error.message);
  } finally {
    spinner.style.display = 'none';
  }
}

function renderSummary(summary) {
  summaryTotal.textContent = summary.total_reviews;
  summaryAverage.textContent = `${summary.average_rating.toFixed(2)}★`;
  summarySentiment.innerHTML = `
    <span class="me-2">${sentimentEmoji.positive} ${summary.sentiment.positive}</span>
    <span class="me-2">${sentimentEmoji.neutral} ${summary.sentiment.neutral}</span>
    <span>${sentimentEmoji.negative} ${summary.sentiment.negative}</span>
  `;
  summaryRecency.textContent = `${summary.recent_reviews} in last ${summary.recent_activity_window_hours}h`;

  keywordsList.innerHTML = '';
  (summary.top_keywords || []).forEach((keyword) => {
    const badge = document.createElement('span');
    badge.className = 'badge text-bg-secondary me-2 mb-2';
    badge.textContent = keyword;
    keywordsList.appendChild(badge);
  });

  if (summary.ai_brief) {
    aiBriefBlock.textContent = summary.ai_brief;
    aiBriefContainer?.classList.remove('d-none');
  } else {
    aiBriefContainer?.classList.add('d-none');
  }
}

function renderReviews(reviews) {
  reviewsTableBody.innerHTML = '';
  if (!reviews.length) {
    const emptyRow = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.textContent = 'No reviews match your filters yet.';
    emptyRow.appendChild(cell);
    reviewsTableBody.appendChild(emptyRow);
    return;
  }

  reviews.forEach((review) => {
    const userComment = review.latest_user_comment || review.comments?.find(c => c.userComment)?.userComment;
    const developerComment = review.latest_developer_comment || review.comments?.find(c => c.developerComment)?.developerComment;

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>
        <div class="fw-semibold">${review.authorName || 'Anonymous'}</div>
        <div class="text-muted small">${userComment?.appVersionName || '—'}</div>
      </td>
      <td>
        <span class="badge text-bg-warning badge-rating">${userComment?.starRating || '—'}★</span>
      </td>
      <td>
        <div>${userComment?.text || '—'}</div>
        ${developerComment?.text ? `<div class="mt-2 small text-success">Developer: ${developerComment.text}</div>` : ''}
      </td>
      <td>
        <div class="small text-muted">👍 ${userComment?.thumbsUpCount || 0}</div>
        <div class="small text-muted">👎 ${userComment?.thumbsDownCount || 0}</div>
      </td>
      <td class="text-muted small">
        ${formatDate(userComment?.lastModified?.seconds)}
      </td>
    `;
    reviewsTableBody.appendChild(row);
  });
}

function formatDate(seconds) {
  if (!seconds) return '—';
  const date = new Date(parseInt(seconds, 10) * 1000);
  return date.toLocaleString();
}

function showAlert(message) {
  const wrapper = document.createElement('div');
  wrapper.innerHTML = `
    <div class="alert alert-danger alert-dismissible" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
  alertPlaceholder.append(wrapper);
}

form.addEventListener('submit', fetchReviews);

// Auto load on page init
fetchReviews();
