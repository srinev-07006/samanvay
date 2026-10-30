const API_BASE = 'http://localhost:8000';

function getHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

export async function fetchInstitutionDetails(institutionId) {
  const res = await fetch(`${API_BASE}/institutions/${institutionId}`, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch institution details');
  return res.json();
}

export async function fetchCaseHistory(institutionId) {
  const data = await fetchInstitutionDetails(institutionId);
  return data.cases || [];
}

export async function fetchOverlapDetails(caseAId, caseBId) {
  const res = await fetch(`${API_BASE}/overlaps/`, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error('Failed to fetch overlaps');
  const data = await res.json();
  if (Array.isArray(data)) {
    return data.filter(o => (o.case_a_id === caseAId && o.case_b_id === caseBId) || (o.case_a_id === caseBId && o.case_b_id === caseAId));
  }
  return [];
}
