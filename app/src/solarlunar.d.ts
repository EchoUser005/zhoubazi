declare module 'solarlunar' {
    interface LunarDate {
      lunarYear: number;
      lunarMonth: number;
      lunarDay: number;
      // Other properties can be added if needed, like isLeap, term, etc.
    }
    interface SolarDate {
      year: number;
      month: number;
      day: number;
      // Other properties can be added if needed.
    }
    export function solar2lunar(year: number, month: number, day: number): LunarDate | -1;
    export function lunar2solar(year: number, month: number, day: number): SolarDate | -1;
  }
  