import ReactDOM from "react-dom/client";
import "./styles/index.scss";
import { RouterProvider } from "react-router-dom";
import { router } from "./routes/index.tsx";
import { ConfigProvider } from "antd";
import zhCN from "antd/locale/zh_CN";
import { validateMessages } from "./config";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <ConfigProvider locale={zhCN} form={{ validateMessages }}>
    <RouterProvider router={router} />
  </ConfigProvider>
);
