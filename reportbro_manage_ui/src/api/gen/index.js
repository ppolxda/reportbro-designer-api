import { generate } from "oig-swagger-tool";
import path from "path";
import process from "process";
import dotenv from "dotenv";

dotenv.config();

const proxy = process.env.VITE_PROXY_URL.endsWith("/")
  ? process.env.VITE_PROXY_URL
  : process.env.VITE_PROXY_URL + "/";

generate({
  url: `${proxy}openapi.json`,
  output: path.resolve(process.cwd(), "./src/api/base-server"),
});
