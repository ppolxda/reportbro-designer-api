import { createBrowserRouter } from "react-router-dom";
import Templates from "@/pages/templates";
import DefaultLayout from "@/layouts/default";

export const router = createBrowserRouter([
  {
    path: import.meta.env.VITE_PUB_PATH,
    element: <DefaultLayout></DefaultLayout>,
    children: [
      {
        index: true,
        element: <Templates></Templates>,
      },
    ],
  },
]);
