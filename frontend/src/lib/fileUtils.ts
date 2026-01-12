export function getFileIcon(filename: string): string {
  const extension = filename.split('.').pop()?.toLowerCase() || '';
  
  const iconMap: Record<string, string> = {
    pdf: '📄',
    docx: '📝',
    doc: '📝',
    txt: '📃',
  };
  
  return iconMap[extension] || '📁';
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const size = bytes / Math.pow(k, i);
  
  return `${size.toFixed(i > 0 ? 1 : 0)} ${units[i]}`;
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}
