/** CardioTwin — Utility Helpers (Olive Green & Red Theme) */

export function getRiskColor(level) {
  const colors = {
    Low: '#556B2F',       // Olive Green
    Moderate: '#85782B',  // Golden Olive
    High: '#C2410C',      // Burnt Red-Amber
    Critical: '#DC2626',  // Alert Red
  };
  return colors[level] || '#64748B';
}

export function getRiskBg(level) {
  const colors = {
    Low: 'rgba(85, 107, 47, 0.12)',
    Moderate: 'rgba(133, 120, 43, 0.12)',
    High: 'rgba(194, 65, 12, 0.12)',
    Critical: 'rgba(220, 38, 38, 0.12)',
  };
  return colors[level] || 'rgba(100, 116, 139, 0.12)';
}

export function getSeverityColor(severity) {
  const colors = {
    critical: '#DC2626',
    high: '#B91C1C',
    moderate: '#85782B',
    low: '#556B2F',
    info: '#606C38',
  };
  return colors[severity] || '#64748B';
}

export function formatNumber(num) {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num.toString();
}

export function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
}

export function getTrendIcon(trend) {
  if (trend === 'rising') return '↑';
  if (trend === 'falling') return '↓';
  return '→';
}
