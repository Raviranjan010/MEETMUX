export function formatDateTime(isoString) {
  if (!isoString) return '--:--';
  const d = new Date(isoString);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}

export function formatDateFull(isoString) {
  if (!isoString) return '---';
  const d = new Date(isoString);
  return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false });
}

export function getDelayBadgeClass(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('on time')) return 'badge-ontime';
  if (cat.includes('low')) return 'badge-low';
  if (cat.includes('moderate')) return 'badge-moderate';
  if (cat.includes('high')) return 'badge-high';
  if (cat.includes('severe')) return 'badge-severe';
  return 'badge-ontime';
}

export function getDelayColor(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('on time')) return '#10B981';
  if (cat.includes('low')) return '#3B82F6';
  if (cat.includes('moderate')) return '#F59E0B';
  if (cat.includes('high')) return '#F97316';
  if (cat.includes('severe')) return '#EF4444';
  return '#94A3B8';
}
