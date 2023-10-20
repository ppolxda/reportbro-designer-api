import { Api } from "./base-server";
export * as ReportType from "./base-server";
import { errorHook, responseHook, timeout } from "./hooks";
import { basePath } from "@/config";

export const reportApi = new Api({
  baseURL: basePath,
  timeout,
});

reportApi.instance.interceptors.response.use(
  (response) => responseHook(response),
  (err) => errorHook(err)
);
