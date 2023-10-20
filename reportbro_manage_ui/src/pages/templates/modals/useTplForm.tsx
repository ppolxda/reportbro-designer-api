import { Form } from "antd";
import { reportApi, ReportType } from "@/api";
import { showCommonModal } from "@/components/commonModal";
import CommonForm from "@/components/commonForm";

interface OpenTplFormProps {
  isAdd: boolean;
  onSuccess?: () => void;
}

export const useTplForm = () => {
  const [form] = Form.useForm<ReportType.TemplateListData>();

  function createTpl() {
    return reportApi.api.apiTemplatesPut(
      form.getFieldsValue(["templateName", "templateType"]),
      {
        successTip: true,
      }
    );
  }

  function openModal(props: OpenTplFormProps) {
    return showCommonModal({
      title: props.isAdd ? "新增模版" : "编辑模版",
      content: (
        <CommonForm
          form={form}
          formItems={[
            { name: "tid", hidden: true },
            {
              label: "模版名称",
              name: "templateName",
              rules: [{ required: true }],
            },
            {
              label: "模版类型",
              name: "templateType",
              rules: [{ required: true }],
            },
          ]}
        />
      ),
      onOk: async () => {
        try {
          await form.validateFields();
          if (props.isAdd) {
            await createTpl();
          } else {
            // TODO: 接口还没出
          }

          props.onSuccess?.();
        } catch {
          return Promise.reject();
        }
      },
      afterClose() {
        form.resetFields();
      },
    });
  }

  return {
    openModal,
    form,
  };
};
