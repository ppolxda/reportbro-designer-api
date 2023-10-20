interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string;
  readonly VITE_APP_GATWAY: string;
  readonly VITE_PUB_PATH: string;
  readonly VITE_PROXY_URL: string;
  readonly VITE_JUMP_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
