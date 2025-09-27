export interface HistoryEntry {
  id: string;
  name: string;
  gender: string;
  birth_location: string;
  is_lunar: boolean;
  birth_time?: string; // For Solar: "YYYY-MM-DD HH:MM:SS"
  year?: number;       // For Lunar
  month?: number;      // For Lunar
  day?: number;        // For Lunar
  time?: string;       // For Lunar: "HH:MM:SS"
  province_code?: string;
  city_code?: string;
  area_code?: string;
}

export const LUNAR_YEARS = Array.from({ length: 150 }, (_, i) => new Date().getFullYear() - i);
export const LUNAR_MONTHS = Array.from({ length: 12 }, (_, i) => i + 1);
export const LUNAR_DAYS = Array.from({ length: 30 }, (_, i) => i + 1);