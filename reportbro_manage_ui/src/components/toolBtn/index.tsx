import { FC } from "react";
import { Button, ButtonProps } from "antd";

export interface ToolBtnProps extends ButtonProps {
  text: string;
}

export const ToolBtn: FC<ToolBtnProps> = (props) => {
  return (
    <Button {...props} type={props.type ?? "primary"}>
      {props.text}
    </Button>
  );
};
