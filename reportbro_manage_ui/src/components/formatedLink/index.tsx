import { jumpUrl } from "@/config";
import { FC } from "react";
import { LinkProps, Link } from "react-router-dom";

export function formatLink(url: string) {
  if (typeof url === "string") {
    return url.replace(
      /^(https?:\/\/[^/]+)/,
      `${(jumpUrl ?? "").replace(/\/$/, "")}`
    );
  }
  return "";
}

const Component: FC<LinkProps> = (props) => {
  const to = formatLink(props.to.toString());

  return (
    <Link {...props} to={to}>
      {to}
    </Link>
  );
};

export default Component;
