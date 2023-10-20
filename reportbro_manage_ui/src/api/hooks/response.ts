import { defaultSuccessTip } from "@/config";
import { AxiosResponse } from "axios";
import { message } from "antd";

export const responseHook = (response: AxiosResponse) => {
  const { config } = response;

  if (typeof config?.responseHook === "function") {
    config.responseHook(response);
  }

  if (config.successTip) {
    message.success({
      content:
        typeof config.successTip === "string"
          ? config.successTip
          : defaultSuccessTip,
      duration: 2,
    });
  }

  return response;
};
