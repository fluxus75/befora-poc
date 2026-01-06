const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined;

const API_BASE_URL = RAW_API_BASE_URL
  ? RAW_API_BASE_URL.replace(/\/+$/, '')
  : '';

export function buildApiUrl(path: string): string {
  if (!path.startsWith('/')) {
    return `${API_BASE_URL}/${path}`;
  }
  return `${API_BASE_URL}${path}`;
}
