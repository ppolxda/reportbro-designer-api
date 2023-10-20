import { Table, TableProps, Space } from "antd";
import { styled } from "styled-components";
import { AnyObject } from "antd/es/_util/type";
import config from "./config";
import { ToolBtn, ToolBtnProps } from "@/components/toolBtn";

export type { TableProps } from "antd";
export type { ColumnsType } from "antd/es/table";

const Wrapper = styled.section`
  padding: 10px;
  .button-wrap {
    margin: 10px 0;
  }
`;

interface ComponentProps<T = any> extends TableProps<T> {
  buttons?: ToolBtnProps[];
}

function Component<T extends AnyObject>(props: ComponentProps<T>) {
  const columns = props.columns?.map((item) => {
    return {
      ...item,
      width: item.width ?? config.defaultColWidth,
      ellipsis: item?.ellipsis ?? true,
    };
  });

  return (
    <Wrapper>
      {props.buttons && (
        <div className="button-wrap">
          <Space wrap>
            {props.buttons.map((btn) => (
              <ToolBtn key={btn.text} {...btn} />
            ))}
          </Space>
        </div>
      )}
      <Table
        {...props}
        columns={columns}
        scroll={props.scroll ?? { x: "100%" }}
      />
    </Wrapper>
  );
}

export default Component;
