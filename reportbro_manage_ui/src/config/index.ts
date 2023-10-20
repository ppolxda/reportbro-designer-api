import type { ValidateMessages } from "rc-field-form/lib/interface";

export const APP_TITLE = import.meta.env.VITE_APP_TITLE; // 页面标题
export const basePath = import.meta.env.VITE_APP_GATWAY || "";
export const jumpUrl = import.meta.env.VITE_JUMP_URL || ""; // 跳转url

export const defaultSuccessTip = "操作成功";

export const validateMessages: ValidateMessages = {
  required: "该字段为必填",
};
