import dayjs from "dayjs";

export enum DATE_FORMAT {
  DATE = "YYYY-MM-DD",
  DATE_TIME = "YYYY-MM-DD HH:mm:ss",
}

export type FormatParam = Parameters<typeof dayjs>[0];

// 格式化时间日期
export function formatDate(value: FormatParam): string {
  if (value) {
    return dayjs(value).format(DATE_FORMAT.DATE);
  }

  return "";
}

// 格式化时间日期
export function formatDateTime(value: FormatParam): string {
  if (value) {
    return dayjs(value).format(DATE_FORMAT.DATE_TIME);
  }

  return "";
}
