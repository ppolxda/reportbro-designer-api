import { FC } from "react";
import { formatDateTime, FormatParam, formatDate } from "@/utils/formatDate";

interface Props {
  value: FormatParam;
}

export const DateTime: FC<Props> = (props) => {
  return <>{formatDateTime(props.value)}</>;
};

export const Date: FC<Props> = (props) => {
  return <>{formatDate(props.value)}</>;
};
