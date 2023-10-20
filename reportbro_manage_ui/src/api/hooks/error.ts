import { message } from "antd";

export const errorHook = async (error: any) => {
  const { config } = error;
  const { data } = error.response;

  let errorTip = "Unknown Error";

  if (typeof data.error === "string") {
    errorTip = data.error;
  }

  if (config.errorTip !== false) {
    message.error({
      content: errorTip,
      type: "error",
    });
  }
};
