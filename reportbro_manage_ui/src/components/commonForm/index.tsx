import { AnyObject } from "antd/es/_util/type";
import {
  FormProps,
  Form,
  Input,
  ConfigProvider,
  FormItemProps,
  InputProps,
} from "antd";
import { validateMessages } from "@/config";
import { omit } from "lodash";

interface FormItem extends FormItemProps {
  component?: React.ReactNode;
  inputProps?: InputProps;
}

interface ComponentProps<T = any> extends FormProps<T> {
  formItems?: FormItem[];
}

function Component<T extends AnyObject>(props: ComponentProps<T>) {
  return (
    <>
      <ConfigProvider form={{ validateMessages }}>
        <Form {...omit(props, ["formItems"])}>
          {(props?.formItems ?? []).map((item) => (
            <Form.Item
              {...omit(item, ["component", "inputProps"])}
              key={item.name?.toString()}
            >
              {item.component ?? <Input {...(item.inputProps ?? {})} />}
            </Form.Item>
          ))}
        </Form>
      </ConfigProvider>
    </>
  );
}

export default Component;
