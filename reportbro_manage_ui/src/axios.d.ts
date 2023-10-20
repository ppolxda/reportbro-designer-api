import { AxiosRequestConfig } from "axios";

declare module "axios" {
  interface AxiosRequestConfig {
    /** 接口报错时是否显示警告，默认为开启  */
    errorTip?: boolean;
    /** 响应返回钩子  */
    responseHook?: (res: AxiosResponse) => void;
    /** 接口返回是否提示「操作成功」，传入字符串则作为自定义提示语 */
    successTip?: boolean | string;
    /** 返回loading状态 */
    progress?: (loading: boolean) => void;
  }
}
