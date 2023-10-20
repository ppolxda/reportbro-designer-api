import { defineConfig, ConfigEnv, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { createHtmlPlugin } from "vite-plugin-html";
import { resolve } from "path";

export default ({ mode }: ConfigEnv) => {
  const { VITE_APP_TITLE, VITE_PROXY_URL, VITE_APP_GATWAY, VITE_PUB_PATH } =
    loadEnv(mode, process.cwd());

  return defineConfig({
    base: VITE_PUB_PATH,
    plugins: [
      react(),
      createHtmlPlugin({
        minify: true,
        inject: {
          data: {
            title: VITE_APP_TITLE,
          },
        },
      }),
    ],
    server: {
      proxy: {
        [VITE_APP_GATWAY]: {
          target: VITE_PROXY_URL,
          rewrite: (path) => path.replace(VITE_APP_GATWAY, ""),
        },
      },
    },
    resolve: {
      alias: {
        "@": resolve(__dirname, "src"),
        "~@": resolve(__dirname, "src"),
      },
    },
  });
};
